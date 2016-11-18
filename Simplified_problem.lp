\* Runway Optimization *\
Minimize
Total_runway_time_used: 100 Variables_h__h + 120 Variables_h__m
 + 90 Variables_m__h + 100 Variables_m__m
Subject To
Number_of_heavys_landed: Variables_h__h + Variables_m__h = 3
Number_of_mediums_landed: Variables_h__m + Variables_m__m = 3
_C1: Variables_h__m + Variables_m__h >= 1
heavys_landing_criterion: Variables_h__m - Variables_m__h + 0 Variables_m__m
 = 0
mediums_landing_criterion: 0 Variables_h__h - Variables_h__m + Variables_m__h
 = 0
Bounds
0 <= Variables_h__h
0 <= Variables_h__m
0 <= Variables_m__h
0 <= Variables_m__m
Generals
Variables_h__h
Variables_h__m
Variables_m__h
Variables_m__m
End
