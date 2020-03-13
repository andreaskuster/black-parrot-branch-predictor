# Black Parrot Branch Predictor



## Simulation
```cd testbench_NAME & make ```

## Wave Form Viewer

``` gtkwave dump.vcd ```


## Prequisites

```
sudo apt install virtualenv build-essential python3-dev gtkwave
```
verilator
iverilog -> icarus

We run our evaluation on:
- `ubuntu 19.10 x86_64 kernel 5.3.0-40-generic`
- `python v3.7`
- `cocotb v1.3.0`
- `verilator v4.020 2019-10-06`


## Testing
http://hpca23.cse.tamu.edu/cbp2016/

https://www.jilp.org/cbp2016/

Test file sizes (#branches):
- short_mobile_1.trace: 16'662'268 
- long_mobile_1.trace:  29'269'647
- short_server_1.trace: 230'692'528
- long_server_1.trace:  149'246'445


## Credits
- https://github.com/black-parrot/black-parrot
- https://cocotb.readthedocs.io/en/latest/index.html
- https://www.veripool.org/wiki/verilator
- https://github.com/antmicro/cocotb-verilator-build
