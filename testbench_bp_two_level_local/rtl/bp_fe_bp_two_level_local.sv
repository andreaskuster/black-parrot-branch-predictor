/*
 * bp_fe_bp_two_level_local.v
 *
 *  Copyright (C) 2020  Andreas Kuster
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
*/
module bp_fe_bp_two_level_local
  #( parameter bht_idx_width_p          = "inv"
   , parameter bp_cnt_sat_bits_p        = "inv"
   , parameter bp_n_hist                = "inv"
   , localparam els_bct_lp              = 2**bht_idx_width_p
   , localparam els_gpt_lp              = 2**bp_n_hist
   , localparam saturation_size_half_lp = ((2** (bp_cnt_sat_bits_p-1))-1) // highest value of the lower half
  )
  ( input                       clk_i
  , input                       reset_i

  , input                       w_v_i
  , input [bht_idx_width_p-1:0] idx_w_i
  , input                       correct_i

  , input                       r_v_i
  , input [bht_idx_width_p-1:0] idx_r_i
  , output                      predict_o
  );

  // branch correlation table (shift registers)
  logic [els_bct_lp-1:0][bp_n_hist-1:0] bct;
  // global pattern table (saturation counters)
  logic [els_gpt_lp-1:0][bp_cnt_sat_bits_p-1:0] gpt;
  // helper signals
  logic taken_pred, taken_actual, count_up_cond, count_down_cond;
  logic [bp_n_hist-1:0] gpt_index_r, gpt_index_w;

  // correlation table shift registers
  always_ff @(posedge clk_i)
    if (reset_i)
      bct <= '{default:0};
    else if (w_v_i)
      bct[idx_w_i] <= {bct[idx_w_i][bp_n_hist-2:0], taken_actual};

  always_comb
    begin
      // level 1 lookup
      gpt_index_w = bct[idx_w_i];
      // level 2 lookup & compare: taken if counter is in upper half
      taken_pred = gpt[gpt_index_w] > saturation_size_half_lp;
      // actual branch outcome
      taken_actual = ((correct_i & taken_pred) | (~correct_i & ~taken_pred));
      // count up if correctly predicted 'taken' or incorrectly predicted 'not taken'
      count_up_cond = w_v_i & taken_actual;
      // count down if correctly predicted 'not taken' or incorrectly predicted 'taken'
      count_down_cond = w_v_i & ~taken_actual;
    end

  // global pattern table: saturating counter, init value: saturation_size_half_lp
  always_ff @(posedge clk_i)
    if (reset_i)
      gpt <= '{default:saturation_size_half_lp};
    else if (count_up_cond & (gpt[gpt_index_w] != {bp_cnt_sat_bits_p{1'b1}}))
      gpt[gpt_index_w] <= gpt[gpt_index_w] + 1;
    else if (count_down_cond & (gpt[gpt_index_w] != 0))
      gpt[gpt_index_w] <= gpt[gpt_index_w] - 1;


  // predict
  // level 1 lookup
  assign gpt_index_r = bct[idx_r_i];
  // level 2 lookup and comparison: taken: (2^N-1) .. (2^N), not taken: 0 .. (2^N-1)-1
  assign predict_o = r_v_i ? (gpt[gpt_index_r] > saturation_size_half_lp) : 1'b0;

endmodule
