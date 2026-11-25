"""Regenerates every CSV in data/ from values transcribed from Romano et al. 2025 + SI."""
import itertools, pandas as pd

LEVELS = {"X1": (3, 5, 7), "X2": (5, 12.5, 20), "X3": (161, 242, 323), "X4": (1.0, 1.5, 2.0)}
def actual(c): return [LEVELS[f"X{i+1}"][int(v)+1] for i, v in enumerate(c)]

# ---- variables -------------------------------------------------------------
pd.DataFrame([
 ["X1","Reaction time","h",3,5,7],
 ["X2","ZnCl2 catalyst loading","mol%",5,12.5,20],
 ["X3","Concentration of 1a","mM",161,242,323],
 ["X4","Equivalents of 2a (PhSe)2","equiv",1.0,1.5,2.0],
], columns=["factor","name","unit","low_m1","centre_0","high_p1"]).to_csv("data/variables.csv", index=False)

# ---- fcCCD (SI Table S3) ----------------------------------------------------
fc = [  # run, LR, X1..X4 coded, Y(% 3a)
(1,"LR072",-1,-1,-1,-1,29),(2,"LR090",1,-1,-1,-1,67),(3,"LR073",-1,1,-1,-1,28),(4,"LR092",1,1,-1,-1,91),
(5,"LR075",-1,-1,1,-1,36),(6,"LR065",1,-1,1,-1,73),(7,"LR028",-1,1,1,-1,51),(8,"LR093",1,1,1,-1,83),
(9,"LR081",-1,-1,-1,1,41),(10,"LR096",1,-1,-1,1,95),(11,"LR082",-1,1,-1,1,38),(12,"LR097",1,1,-1,1,100),
(13,"LR085",-1,-1,1,1,57),(14,"LR126",1,-1,1,1,67),(15,"LR086",-1,1,1,1,48),(16,"LR099",1,1,1,1,100),
(17,"LR119",0,0,0,0,68),(18,"LR127",1,0,0,0,100),(19,"LR105",-1,0,0,0,35),(20,"LR120",0,1,0,0,48),
(21,"LR121",0,-1,0,0,34),(22,"LR122",0,0,1,0,55),(23,"LR087",0,0,-1,0,93),(24,"LR123",0,0,0,1,75),
(25,"LR124",0,0,0,-1,57)]
def block(rows, label):
    out=[]
    for r in rows:
        c=r[2:6]; a=actual(c)
        out.append(dict(design=label, run=r[0], lab_ref=r[1], X1_c=c[0],X2_c=c[1],X3_c=c[2],X4_c=c[3],
                        X1_time_h=a[0],X2_ZnCl2_mol=a[1],X3_conc_mM=a[2],X4_equiv_2a=a[3], Y_pct_3a=r[6]))
    return pd.DataFrame(out)
def kind(c):
    n0=sum(1 for v in c if v==0)
    return "factorial" if n0==0 else ("centre" if n0==4 else "axial")
d1=block(fc,"fcCCD"); d1["point_type"]=[kind(t) for t in d1[["X1_c","X2_c","X3_c","X4_c"]].values]
d1.to_csv("data/fcccd_runs.csv", index=False)

# ---- D-optimal (SI Table S4; Y as printed in the SI) ------------------------
do = [
(1,"LR072",-1,-1,-1,-1,29),(2,"LR073",-1,1,-1,-1,28),(3,"LR092",1,1,-1,-1,91),(4,"LR077",0,-1,0,-1,36),
(5,"LR065",1,-1,1,-1,73),(6,"LR076",-1,0,1,-1,63),(7,"LR079/LR102",0,1,1,-1,59),(8,"LR087/LR122",0,0,-1,0,78),
(9,"LR157",-1,1,0,0,37),(10,"LR106",-1,-1,1,0,39),(11,"",1,1,1,0,87),(12,"LR081",-1,-1,-1,1,41),
(13,"LR096",1,-1,-1,1,95),(14,"LR097",1,1,-1,1,100),(15,"LR129",1,0,0,1,100),(16,"LR125",0,-1,1,1,57),
(17,"LR086",-1,1,1,1,48)]
d2=block(do,"D-optimal")
fcset={tuple(r) for r in d1[["X1_c","X2_c","X3_c","X4_c"]].values}
d2["also_in_fcCCD"]=[tuple(r) in fcset for r in d2[["X1_c","X2_c","X3_c","X4_c"]].values]
d2.to_csv("data/doptimal_runs.csv", index=False)

# ---- coefficients -----------------------------------------------------------
terms=["b0","b1 (X1)","b2 (X2)","b3 (X3)","b4 (X4)","b12","b13","b14","b23","b24","b34","b11 (X1^2)","b22 (X2^2)","b33 (X3^2)","b44 (X4^2)"]
fc_c=[63.0508,22.9444,4.8889,-0.6667,5.8889,4.375,-5.375,0.5,1.5,-1.375,-1.875,5.2740,-21.2260,11.7740,3.7740]
fc_sd=[1.0536]+[0.5751]*4+[0.6100]*6+[1.5290]*4
fc_ci=[2.2955]+[1.2531]*4+[1.3291]*6+[3.3313]*4
fc_p=[0,0,0,.2689,0,0,0,.4284,.0301,.0437,.0096,.0048,0,0,.0296]
fc_rsd=[8.977,3.998,3.664,4.817,3.685]+[4.099]*6+[13.734,10.605,20.082,10.819]
fc_rp=[0,0,.1941,.8910,.1226,.2960,.2017,.9039,.7175,.7401,.6513,.7042,.0563,.5629,.7301]
do_c=[68.3104,23.3786,3.3604,-0.4624,4.1809,1.0561,-4.8681,-0.3343,1.2845,-0.9907,-1.8589,6.7033,-20.3780,9.4023,-1.1005]
do_sd=[2.2015,.7657,.7292,.7303,.7657,.7998,.8333,.8773,.7792,.7998,.8333,1.5216,1.7380,1.7245,1.5216]
do_ci=[6.1123,2.1259,2.0246,2.0275,2.1259,2.2205,2.3135,2.4358,2.1633,2.2205,2.3135,4.2247,4.8254,4.7880,4.2247]
do_p=[0,0,.0100,.5610,.0055,.2572,.0043,.7225,.1746,.2832,.0895,.0116,.0003,.0055,.5096]
do_vif=[None,1.274,1.250,1.254,1.274,1.175,1.276,1.262,1.224,1.175,1.276,1.190,1.253,1.234,1.190]
do_rsd=[36.374,8.981,13.941,11.344,14.324,12.747,10.568,15.157,13.956,17.269,15.441,21.345,26.796,19.751,20.266]
do_rp=[.0776,.0186,.8124,.9680,.7739,.9349,.6509,.9827,.9277,.9549,.9056,.7573,.4574,.6401,.9573]
fc_vif=[None]+[1.0]*10+[1.979]*4
rows=[]
for i,t in enumerate(terms):
    rows.append(dict(term=t,fcCCD_coef=fc_c[i],fcCCD_sd=fc_sd[i],fcCCD_ci=fc_ci[i],fcCCD_p=fc_p[i],fcCCD_vif=fc_vif[i],
        fcCCD_resamp_sd=fc_rsd[i],fcCCD_resamp_p=fc_rp[i],
        Dopt_coef=do_c[i],Dopt_sd=do_sd[i],Dopt_ci=do_ci[i],Dopt_p=do_p[i],Dopt_vif=do_vif[i],
        Dopt_resamp_sd=do_rsd[i],Dopt_resamp_p=do_rp[i]))
pd.DataFrame(rows).to_csv("data/coefficients.csv", index=False)

# ---- model statistics -------------------------------------------------------
pd.DataFrame([
 ["Number of runs",25,17,""],["Model coefficients",15,15,""],["Residual degrees of freedom",10,2,"runs - coefficients"],
 ["Variance of Y",587,660.3,"SI"],["Residual SD (%)",11.8,4.982,"SI"],
 ["Adjusted R2 (%)",76.29,96.24,"SI label: % explained variance; matches adjusted R2 (recomputed)"],["Raw R2 (%)",90.12,99.53,"recomputed from the run tables"],["RMSECV (%)",18.15,33.6,"SI, leave-one-out"],
 ["CV explained variance Q2 (%)",43.86,-70.98,"SI"],["Max VIF (quadratic terms)",1.979,1.276,"SI; D-opt max over all terms"],
 ["Trace of dispersion matrix",2.3543,3.6539,"SI"],["Experimental variance used (s2)",2.44,2.44,"main text: centre-point replicates"],
], columns=["metric","fcCCD","D-optimal","note"]).to_csv("data/model_stats.csv", index=False)

# ---- preliminary screening (SI Table S1) -----------------------------------
pre=[(1,"CH3CN","Blue LED","Zn(OTf)2",5,3,31),(2,"CH3CN","Dark","Zn(OTf)2",5,3,None),(3,"CH3CN","Sunlight","Zn(OTf)2",5,3,None),
(4,"DMF","Blue LED","Zn(OTf)2",5,4,32),(5,"DMF","Dark","Zn(OTf)2",5,4,None),(6,"THF","Blue LED","Zn(OTf)2",5,4,29),
(7,"THF","Dark","Zn(OTf)2",5,4,None),(8,"CH3CN","Blue LED","ZnCl2",5,3,36),(9,"CH3CN","Blue LED","none",0,3,15)]
pd.DataFrame(pre,columns=["entry","solvent","light","catalyst","catalyst_mol_pct","time_h","conversion_pct"]).to_csv("data/preliminary_screening.csv",index=False)

# ---- FlowNMR kinetics (SI Table S5; 3a % read from the table, 1a = 100 - 3a) --
p3=[0,0,0,4,3,5,6,7,8,9, 10,11,13,15,16,16,16,17,17,19, 20,21,23,23,24,25,26,28,28,30,
31,32,33,33,35,36,36,37,38,40, 41,42,42,43,44,46,47,47,49,48, 50,52,53,53,54,56,57,56,58,58,
60,60,61,62,62,64,66,66,66,68, 68,68,70,71,71,73,74,75,76,76, 76,78,79,78,79,80,81,82,82,84,
84,85,86,86,87,88,88,89,89,90, 91,92,93,94,96,95,95,97,97,100]
assert len(p3)==110
pd.DataFrame(dict(time_min=[5*i for i in range(110)],spectrum_no=[10+i for i in range(110)],
   pct_1a=[100-v for v in p3],pct_3a=p3)).to_csv("data/flownmr_kinetics.csv",index=False)

# ---- mechanism controls -----------------------------------------------------
pd.DataFrame([
 ["Standard conditions, air (Table 2 entry 14: 7 h, 5 mol%, 323 mM, 2 equiv)","air",67,"fcCCD run 14"],
 ["Same, argon atmosphere","argon",10,"Fig. S6"],
 ["Same, O2 atmosphere","oxygen",84,"Fig. S6"],
 ["Radical trap TEMPO added (standard conditions)","air + TEMPO",85,"yield of 3a, main text"],
], columns=["experiment","atmosphere_or_additive","conversion_or_yield_pct","source"]).to_csv("data/mechanism_controls.csv",index=False)

# ---- scope ------------------------------------------------------------------
pd.DataFrame([
 ["3a","N-methylindole","(PhSe)2",100,"quantitative; model reaction"],
 ["3b","N-methylindole","(PhS)2",11,"S much worse than Se"],
 ["3d","indole (N-H)","(PhSe)2",98,""],
 ["3f","N-methylindole","(BnSe)2",20,"lower yield"],
 ["3h","N,N-dimethylaniline","(PhSe)2",45,"fair"],
 ["3i","1,3,5-trimethoxybenzene","(PhSe)2",7,"poor"],
 ["-","N-acetylindole","(PhSe)2",0,"no reaction (EWG on N)"],
 ["-","N-methylindole","(PhTe)2",0,"no reaction"],
 ["-","N-methylindole","DSBA",0,"no reaction (carboxylic acid)"],
], columns=["product","substrate","dichalcogenide","yield_pct","comment"]).to_csv("data/scope.csv",index=False)
print("done")
