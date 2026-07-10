from qkernel.export_circuit import WeylProgram, export_qiskit_protocol, tight_nc_bound
OBS={"XI":[0,1,0,0],"IX":[0,0,0,1],"XX":[0,1,0,1],"IZ":[0,0,1,0],"ZI":[1,0,0,0],
     "ZZ":[1,0,1,0],"XZ":[0,1,1,0],"ZX":[1,0,0,1],"YY":[1,1,1,1]}
CTX=[["XI","IX","XX"],["IZ","ZI","ZZ"],["XZ","ZX","YY"],
     ["XI","IZ","XZ"],["IX","ZI","ZX"],["XX","ZZ","YY"]]
def test_pm_tight_bound_is_four():
    prog=WeylProgram(d=2,m=2,observables=OBS,contexts=CTX)
    assert tight_nc_bound([[ "XI","IX","XX"],["IZ","ZI","ZZ"],["XZ","ZX","YY"],["XI","IZ","XZ"],["IX","ZI","ZX"],["XX","ZZ","YY"]],[1,1,1,1,1,-1])==4.0
    assert "NC_BOUND = 4.0" in export_qiskit_protocol(prog).script
def test_loose_fallback_unreachable_for_pm():
    prog=WeylProgram(d=2,m=2,observables=OBS,contexts=CTX)
    assert tight_nc_bound(CTX,[1]*6)==6.0  # all-satisfiable pattern -> bound = nc
