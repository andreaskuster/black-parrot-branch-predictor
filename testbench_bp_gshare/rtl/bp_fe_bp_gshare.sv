/*
 * bp_fe_bp_gshare.v
*/
module bp_fe_bp_gshare
  #( parameter bht_idx_width_p          = "inv"
   , parameter bp_cnt_sat_bits_p        = "inv"
   , localparam els_lp                  = 2**bht_idx_width_p
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

  // branch history table
  logic [els_lp-1:0][bp_cnt_sat_bits_p-1:0] bht;

  // helper signals: taken prediction, count up condition, count down condition, taken feedback hw
  logic taken_pred, count_up_cond, count_down_cond, taken_actual;

  // global history
  logic [bht_idx_width_p-1:0] gh;

  // address hash
  logic [bht_idx_width_p-1:0] idx_w, idx_r;

  // global history shift register
  always_ff @(posedge clk_i)
    if (reset_i)
      gh <= 0;
    else if (w_v_i)
      gh <= {gh[bht_idx_width_p-2:0], taken_actual};

  // compute access indices
  always_comb
    begin
      idx_w = gh ^ idx_w_i;
      idx_r = gh ^ idx_r_i;
    end

  always_comb
    begin
      // taken if counter is in upper half
      taken_pred = bht[idx_w] > saturation_size_half_lp;
      // taken feedback from hw
      taken_actual = (correct_i & taken_pred) | (~correct_i & ~taken_pred);
      // count up if correctly predicted 'taken' or incorrectly predicted 'not taken'
      count_up_cond = w_v_i & ((correct_i & taken_pred) | (~correct_i & ~taken_pred));
      // count down if correctly predicted 'not taken' or incorrectly predicted 'taken'
      count_down_cond = w_v_i & ((correct_i & ~taken_pred) | (~correct_i & taken_pred));
    end

  // saturating counter, init value: saturation_size_half_lp
  always_ff @(posedge clk_i)
    if (reset_i)
      bht <= '{default:saturation_size_half_lp};
    else if (count_up_cond & (bht[idx_w] != {bp_cnt_sat_bits_p{1'b1}}))
      bht[idx_w] <= bht[idx_w] + 1;
    else if (count_down_cond & (bht[idx_w] != 0))
      bht[idx_w] <= bht[idx_w] - 1;

  // predict
  // taken: (2^N-1) .. (2^N)
  // not taken: 0 .. (2^N-1)-1
  assign predict_o = r_v_i ? (bht[idx_r] > saturation_size_half_lp) : 1'b0;

endmodule
