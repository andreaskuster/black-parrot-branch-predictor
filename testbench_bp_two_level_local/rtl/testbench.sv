// testbench DUT
module testbench
  #( parameter bht_idx_width_p   = 2
  ,  parameter bp_cnt_sat_bits_p = 2
  ,  parameter bp_n_hist         = 2
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

  // instantiate two-level local predictor
  bp_fe_bp_two_level_local
   #( .bht_idx_width_p(bht_idx_width_p)
    , .bp_cnt_sat_bits_p(bp_cnt_sat_bits_p)
    , .bp_n_hist(bp_n_hist)
    )
    bp
    ( .clk_i(clk_i)
    , .reset_i(reset_i)

    , .w_v_i(w_v_i)
    , .idx_w_i(idx_w_i)
    , .correct_i(correct_i)

    , .r_v_i(r_v_i)
    , .idx_r_i(idx_r_i)
    , .predict_o(predict_o)
  );


`ifndef VERILATOR
  // dump waves
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(1, testbench);
  end
`endif

endmodule
