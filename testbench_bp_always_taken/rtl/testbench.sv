// testbench DUT
module testbench
  #( parameter bht_idx_width_p   = "inv"
  ,  parameter bp_cnt_sat_bits_p = "inv"
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

  bp_fe_bp_always_taken bp
  ( .r_v_i(r_v_i)
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
