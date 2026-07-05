# Generated paper benchmark tables

Generated from `experiments/output/*.csv`.

## Decomposition benchmark

| noise | ctx | obs | comp | kernel ctx | decomp ms | global ms | same |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 6 | 9 | 1 | 6 | 0.1753 | 0.1554 | True |
| 10 | 16 | 39 | 11 | 6 | 0.3401 | 0.3777 | True |
| 50 | 56 | 159 | 51 | 6 | 1.0351 | 2.6312 | True |
| 100 | 106 | 309 | 101 | 6 | 1.9503 | 8.6265 | True |
| 500 | 506 | 1509 | 501 | 6 | 10.5471 | 242.1095 | True |


## Solver comparison

| case | solver | ctx | obs | contextual | kernel ctx | verified | ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pm_plus_0_disconnected | span | 6 | 9 | True | 6 | True | 0.1775 |
| pm_plus_0_disconnected | bounded_weight_6 | 6 | 9 | True | 6 | True | 0.1665 |
| pm_plus_0_disconnected | branch_bound | 6 | 9 | True | 6 | True | 0.169 |
| pm_plus_0_disconnected | auto | 6 | 9 | True | 6 | True | 0.1679 |
| pm_plus_100_disconnected | span | 106 | 309 | True | 6 | True | 1.7172 |
| pm_plus_100_disconnected | bounded_weight_6 | 106 | 309 | True | 6 | True | 1.5984 |
| pm_plus_100_disconnected | branch_bound | 106 | 309 | True | 6 | True | 1.6463 |
| pm_plus_100_disconnected | auto | 106 | 309 | True | 6 | True | 2.0006 |
| pm_plus_10_connected_ladder | span | 16 | 29 | True | 6 | True | 0.2962 |
| pm_plus_10_connected_ladder | bounded_weight_6 | 16 | 29 | True | 6 | True | 2.3851 |
| pm_plus_10_connected_ladder | branch_bound | 16 | 29 | True | 6 | True | 0.2712 |
| pm_plus_10_connected_ladder | auto | 16 | 29 | True | 6 | True | 0.3595 |

