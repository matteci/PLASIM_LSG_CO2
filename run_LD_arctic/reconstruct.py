import sys
import numpy as np
from scipy import io
import subprocess

# read input
script=sys.argv[0]
expdir=sys.argv[1]
expname=sys.argv[2]
ntrajs=int(sys.argv[3])
lenblocks=int(sys.argv[4])
initblock=int(sys.argv[5])
endblock=int(sys.argv[6])

# define folders as in main script (many are not actually needed)
resamplingexpdir=expdir+'/resampling'

# define number of blocks
nblocks=endblock-initblock+1

# for filename in os.listdir(resamplingexpdir):
#     if filename.endswith(".tar"):
#         tar -xvf filename
#     else:
#         continue

# define label arrays. initlabel_ens containes the initlabels for each block, while initlabel_eff contains the effective genealogy of the trajectories
initlabelnow=np.arange(ntrajs)
initlabelold=np.arange(ntrajs)
initlabel_ens=np.empty((ntrajs,nblocks))
initlabel_eff=np.empty((ntrajs,nblocks))
# define array of kill counters. killedlabel_eff should be made of all zeros and it is stored as a test
killedcount=np.empty(nblocks)
killedlabel_ens=np.empty((ntrajs,nblocks))
killedlabel_eff=np.empty((ntrajs,nblocks))
# define control observable ensembles
obsts_ens=np.empty((ntrajs,nblocks*lenblocks))
obsts_eff=np.empty((ntrajs,nblocks*lenblocks))
obsmean_ens=np.empty((ntrajs,nblocks))
obsmean_eff=np.empty((ntrajs,nblocks))
# ensembles of various algorithm variables, as a test 
Nc_ens=np.empty(nblocks)
R_ens=np.empty(nblocks)
W_ens=np.empty((ntrajs,nblocks))
W_eff=np.empty((ntrajs,nblocks))
w_ens=np.empty((ntrajs,nblocks))
w_eff=np.empty((ntrajs,nblocks))
nc_ens=np.empty((ntrajs,nblocks))
nc_eff=np.empty((ntrajs,nblocks))


### IMPORTANT PART
# AVRÒ MATRICE CON RIGHE TRAIETTORIE, COLONNE QUALÈ TRAIETTORIA DA PRENDERE
# backward loop over the blocks. given the way python works the range looks weird, but it is correct 
for block in range((endblock-1),-1,(initblock-2)): # parte dal fondo
    print(block)
    block_label=str(block+1)
    # extract data from the current block
    # resamplingdata=np.load(resamplingexpdir+'/block_'+block_label.zfill(4)+'/'+expname+'_resampling.'+block_label.zfill(4)+'.npz')
    # Arctic_LD_icev_abs_ntraj96_k10_LBlock5_LRun225_p1_startID0001
    resamplingdata=np.load(resamplingexpdir+'/'+expname+'_resampling.'+block_label.zfill(4)+'.npz')
    obsts=resamplingdata['obsts']
    obsmean=resamplingdata['obsmean']
    initlabel=resamplingdata['initlabel']     # GUARDA IN FUNZIONE RESAMPLING: VETTORE CON LUNGHEZZA #TRAJ (indice nuova traiettoria)
    killedlabel=resamplingdata['killedlabel'] # 
    Nc=resamplingdata['Nc']
    W=resamplingdata['W']  # W: W=np.exp(k*(obsmean')) specify traj and block
    R=resamplingdata['R']  # R: average of W across trajs for a block (normalizer)
    w=resamplingdata['w']  # w: W normalised by R
    nc=resamplingdata['nc']
    # compute the *_ens fields     
    initlabel_ens[:,block]=initlabel[:]
    killedlabel_ens[:,block]=killedlabel[:]
    obsts_ens[:,block*lenblocks:(block+1)*lenblocks]=obsts[:,:]
    obsmean_ens[:,block]=obsmean[:]  # ensemble
    Nc_ens[block]=Nc
    R_ens[block]=R
    W_ens[:,block]=W[:]
    w_ens[:,block]=w[:]
    nc_ens[:,block]=nc[:]
    # compute the labels for the reconstruction. the labels are updated keeping track of the labels of the previous (actually following) block
    initlabelnow[:]=initlabel[initlabelold]
    initlabelold[:]=initlabelnow[:]
    # compute the *_eff fields 
    initlabel_eff[:,block]=initlabelnow[:]  ### matrice (righe x blocchi)
    killedlabel_eff[:,block]=killedlabel[initlabelnow[:]]
    obsts_eff[:,block*lenblocks:(block+1)*lenblocks]=obsts[initlabelnow[:],:]
    obsmean_eff[:,block]=obsmean[initlabelnow[:]] # reconstructed ensemble
    W_eff[:,block]=W[initlabelnow[:]] ## numeratore peso
    w_eff[:,block]=w[initlabelnow[:]] ## numeratore peso normalizzato da somma su traiettorie
    nc_eff[:,block]=nc[initlabelnow[:]]

# gli R deveono essere calcolati sui W_ens

# save data
# versione ens: senza ricostruzione
# versione eff: con ricostruzione
# con i pesi poi calcoli la statistica
fileout=resamplingexpdir+'/'+expname+'_resampling.'+str(initblock).zfill(4)+'_'+str(endblock).zfill(4)
np.savez(resamplingexpdir+'/'+expname+'_resampling.'+str(initblock).zfill(4)+'_'+str(endblock).zfill(4),\
         ntrajs=ntrajs,lenblocks=lenblocks,W_ens=W_ens,W_eff=W_eff,w_ens=w_ens,w_eff=w_eff,nc_ens=nc_ens,nc_eff=nc_eff,\
         killedlabel_ens=killedlabel_ens,killedlabel_eff=killedlabel_eff,initlabel_ens=initlabel_ens,initlabel_eff=initlabel_eff,\
         obsts_ens=obsts_ens,obsts_eff=obsts_eff,obsmean_ens=obsmean_ens,obsmean_eff=obsmean_eff)

#
gg=dict()
gg['ntrajs']=ntrajs
gg['lenblocks']=lenblocks
gg['W_ens']=W_ens
gg['W_eff']=W_eff
gg['w_ens']=w_ens
gg['w_eff']=w_eff
gg['R_ens']=R_ens
gg['nc_ens']=nc_ens
gg['nc_eff']=nc_eff
gg['killedlabel_ens']=killedlabel_ens
gg['killedlabel_eff']=killedlabel_eff
gg['initlabel_ens']=initlabel_ens
gg['initlabel_eff']=initlabel_eff
gg['obsts_ens']=obsts_ens
gg['obsts_eff']=obsts_eff
gg['obsmean_ens']=obsmean_ens
gg['obsmean_eff']=obsmean_eff
io.savemat(fileout,mdict = gg)

# clean
subprocess.call('rm '+resamplingexpdir+'/'+expname+'_resampling.????.npz', shell=True)        


