/*
 * bp_fe_bp_tournament.v
*/
module bp_fe_bp_tournament
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

  //
  // LOCAL BRANCH PREDICTOR 0
  // branch history table
  logic [els_lp-1:0][bp_cnt_sat_bits_p-1:0] bht_local;
  // helper signals
  logic predict_local, taken_pred_local, taken_actual_local, local_correct;

  //
  // GLOBAL BRANCH PREDICTOR 1
  // branch history table
  logic [els_lp-1:0][bp_cnt_sat_bits_p-1:0] bht_global;
  // global history
  logic [bht_idx_width_p-1:0] gh;
  // helper signals
  logic predict_global, taken_pred_global, taken_actual_global, global_correct;

  //
  // SELECTOR
  // branch history table
  logic [bp_cnt_sat_bits_p-1:0] bht_sel;
  // helper signals
  logic predict_selection;

  // 
  // GENERAL
  // helper signals
  logic count_down_cond, count_up_cond, count_up_cond_sel, count_down_cond_sel, taken_actual;


  //
  // LOCAL BRANCH PREDICTOR 0

  // update
  // saturating counter, init value: saturation_size_half_lp
  always_ff @(posedge clk_i)
    if (reset_i)
      bht_local <= '{default:saturation_size_half_lp};
    else if (count_up_cond & (bht_local[idx_w_i] != {bp_cnt_sat_bits_p{1'b1}}))
      bht_local[idx_w_i] <= bht_local[idx_w_i] + 1;
    else if (count_down_cond & (bht_local[idx_w_i] != 0))
      bht_local[idx_w_i] <= bht_local[idx_w_i] - 1;
  
  // predict
  // taken: (2^N-1) .. (2^N), not taken: 0 .. (2^N-1)-1
  assign predict_local = bht_local[idx_r_i] > saturation_size_half_lp;


  //
  // GLOBAL BRANCH PREDICTOR 1

  // update
  // saturating counter, init value: saturation_size_half_lp
  always_ff @(posedge clk_i)
    if (reset_i)
      bht_global <= '{default:saturation_size_half_lp};
    else if (count_up_cond & (bht_global[gh] != {bp_cnt_sat_bits_p{1'b1}}))
      bht_global[gh] <= bht_global[gh] + 1;
    else if (count_down_cond & (bht_global[gh] != 0))
      bht_global[gh] <= bht_global[gh] - 1;
  // global history shift register
  always_ff @(posedge clk_i)
    if (reset_i)
      gh <= 0;
    else if (w_v_i)
      gh <= {gh[bht_idx_width_p-2:0], taken_actual};

  // predict
  // taken: (2^N-1) .. (2^N), not taken: 0 .. (2^N-1)-1
  assign predict_global = bht_global[gh] > saturation_size_half_lp;


  //
  // SELECTOR
  
  // update
  always_ff @(posedge clk_i)
    if (reset_i)
      bht_sel <= saturation_size_half_lp;
    else if (count_up_cond_sel & (bht_sel != {bp_cnt_sat_bits_p{1'b1}}))
      bht_sel <= bht_sel + 1;
    else if (count_down_cond_sel & (bht_sel != 0))
      bht_sel <= bht_sel - 1;

  // predict
  assign predict_selection = (bht_sel > saturation_size_half_lp) ? predict_global : predict_local;
  assign predict_o = r_v_i ? predict_selection : 1'b0;


  //
  // GENERAL
  always_comb
    begin
      // local prediction
      taken_pred_local = bht_local[idx_w_i] > saturation_size_half_lp;
      taken_actual_local = (correct_i & taken_pred_local) | (~correct_i & ~taken_pred_local);
      // global prediction
      taken_pred_global = bht_global[gh] > saturation_size_half_lp;
      taken_actual_global = (correct_i & taken_pred_global) | (~correct_i & ~taken_pred_global);
      // actual outcome
      taken_actual = (bht_sel > saturation_size_half_lp) ? taken_actual_global: taken_actual_local;
      // count up / down condition
      count_up_cond = w_v_i & taken_actual;
      count_down_cond = w_v_i & ~taken_actual;
      // check correctness of prediction from pb0 and pb1
      local_correct = (taken_actual == taken_pred_local);
      global_correct = (taken_actual == taken_pred_global);
      // selector count condition
      count_up_cond_sel = w_v_i & ~local_correct & global_correct;
      count_down_cond_sel = w_v_i & local_correct & ~global_correct;
    end


endmodule

