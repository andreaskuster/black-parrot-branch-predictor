// adder DUT
module adder
  #(
     parameter  DATA_WIDTH = 6
  ) 
  (  input                       clk_i
   , input                       rst_i
   , input      [DATA_WIDTH-1:0] a_i
   , input      [DATA_WIDTH-1:0] b_i
   , output reg [DATA_WIDTH:0]   sum_o
  );

  always_ff @(posedge clk_i) begin
    if (rst_i)
      sum_o <= 0;
    else
      sum_o <= a_i + b_i;
  end

`ifndef VERILATOR
  // dump waves
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(1, adder);
  end
`endif

endmodule
