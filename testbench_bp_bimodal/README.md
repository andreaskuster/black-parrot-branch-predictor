## Bimodal Evaluation

![](../evaluation/plots/bimodal_short_mobile_1.png)

![](../evaluation/plots/bimodal_long_mobile_1.png)

![](../evaluation/plots/bimodal_short_server_1.png)

![](../evaluation/plots/bimodal_long_server_1.png)

There are two main observations:
- Saturating counters should probably have two or three bits and the get worse with more, most likely due to the longer 
learning/re-learning phase.
- The (default) behaviour of hash functions: the bigger the image size to map into, the less collisions 
and therefore the higher the accuracy.