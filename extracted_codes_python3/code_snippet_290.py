# -*- coding: utf-8 -*-
"""
.. _force-training-example:

Train Neural Network Potential To Both Energies and Forces
==========================================================

We have seen how to train a neural network potential by manually writing
training loop in :ref:`training-example`. This tutorial shows how to modify
that script to train to force.
"""

###############################################################################
# Most part of the script are the same as :ref:`training-example`, we will omit
# the comments for these parts. Please refer to :ref:`training-example` for more
# information

import torch
import torchani
import os
import math
import torch.utils.tensorboard
import tqdm

# helper function to convert energy unit from Hartree to kcal/mol
from torchani.units import hartree2kcalmol


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#device = torch.device('cpu')
"""
Rcr = 5.1000e+00
Rca = 3.5000e+00
EtaR = torch.tensor([1.9700000e+01], device=device)
ShfR = torch.tensor([8.0000000e-01,1.0687500e+00,1.3375000e+00,1.6062500e+00,1.8750000e+00,2.1437500e+00,2.4125000e+00,2.6812500e+00,2.9500000e+00,3.2187500e+00,3.4875000e+00,3.7562500e+00,4.0250000e+00,4.2937500e+00,4.5625000e+00,4.8312500e+00], device=device)
Zeta = torch.tensor([1.4100000e+01], device=device)
ShfZ = torch.tensor([3.9269908e-01,1.1780972e+00,1.9634954e+00,2.7488936e+00], device=device)
EtaA = torch.tensor([1.2500000e+01], device=device)
ShfA = torch.tensor([8.0000000e-01,1.1375000e+00,1.4750000e+00,1.8125000e+00,2.1500000e+00,2.4875000e+00,2.8250000e+00,3.1625000e+00], device=device)
species_order = ['C']
num_species = len(species_order)
aev_computer = torchani.AEVComputer(Rcr, Rca, EtaR, ShfR, EtaA, Zeta, ShfA, ShfZ, num_species)
"""

#energy_shifter = torchani.utils.EnergyShifter(None)
###############################################################################
# Now let's read self energies and construct energy shifter.
try:
    path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    path = os.getcwd()
    
sae_file = os.path.join(path, 'sae_linfit_dftb.dat')  # noqa: E501
#sae_file = os.path.join(path, 'sae_linfit_ani.data')  # noqa: E501
const_file = os.path.join(path, 'rC.params')

consts = torchani.neurochem.Constants(const_file)
aev_computer = torchani.AEVComputer(**consts)

#min_cell=torch.tensor([[20.0,0,0],[0,20.0,0],[0,0,20.0]],requires_grad=True,dtype=torch.float64,device=device)
#aev_computer.setMinCell(min_cell)

energy_shifter = torchani.neurochem.load_sae(sae_file)
species_order = ['H','C']

#print('Self atomic energies: ', energy_shifter.self_energies)
#dspath = os.path.join(path, 'ch4.h5')
#dspath = os.path.join(path, 'gra4.h5')
#dspath = os.path.join(path, 'mx0.05.h5')
#dspath = os.path.join(path, 'gra.h5')
#dspath = os.path.join(path, 'gra_min.h5') #min x,y,z
#dspath = os.path.join(path, 'gra_wmin.h5') #min x,y,z, wo min x,y,bi
trpath = os.path.join(path, 'train.h5') #min x,y,z, wo min x,y,bi
valpath = os.path.join(path, 'validation.h5') #min x,y,z, wo min x,y,bi

#batch_size = 1068 #first epoch
batch_size = 64 #second epoch
#batch_size = 256 #second epoch

"""
training, validation = torchani.data.load(
    dspath,
    additional_properties=('forces','cell')
).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle().split(0.8, None)
"""

training = torchani.data.load(
    trpath,
    additional_properties=('forces','cell')
).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()

validation = torchani.data.load(
    valpath,
    additional_properties=('forces','cell')
).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()

training = training.collate(batch_size).cache()
validation = validation.collate(batch_size).cache()

#print('Self atomic energies: ', energy_shifter.self_energies)
pbc = torch.tensor([1,1,1],dtype=torch.bool,device=device)
###############################################################################
# The code to define networks, optimizers, are mostly the same
aev_dim = aev_computer.aev_length

H_network = torch.nn.Sequential(
    torch.nn.Linear(aev_dim, 256),
    torch.nn.GELU(),
    torch.nn.Linear(256, 192),
    torch.nn.GELU(),
    torch.nn.Linear(192, 160),
    torch.nn.GELU(),
    torch.nn.Linear(160, 1)
)

C_network = torch.nn.Sequential(
    torch.nn.Linear(aev_dim, 224),
    torch.nn.GELU(),
    torch.nn.Linear(224, 192),
    torch.nn.GELU(),
    torch.nn.Linear(192, 160),
    torch.nn.GELU(),
    torch.nn.Linear(160, 1)
)

nn = torchani.ANIModel([H_network,C_network])


###############################################################################
# Initialize the weights and biases.
#
# .. note::
#   Pytorch default initialization for the weights and biases in linear layers
#   is Kaiming uniform. See: `TORCH.NN.MODULES.LINEAR`_
#   We initialize the weights similarly but from the normal distribution.
#   The biases were initialized to zero.
#
# .. _TORCH.NN.MODULES.LINEAR:
#   https://pytorch.org/docs/stable/_modules/torch/nn/modules/linear.html#Linear


def init_params(m):
    if isinstance(m, torch.nn.Linear):
        torch.nn.init.kaiming_normal_(m.weight, a=1.0)
        torch.nn.init.zeros_(m.bias)

nn.apply(init_params)

"""
ori_model = torchani.models.ANI2x(periodic_table_index=True).to(device).to(torch.float64)
layers = list(ori_model.children())
nn.load_state_dict(layers[2].state_dict(),strict=False)
"""
###############################################################################
# Let's now create a pipeline of AEV Computer --> Neural Networks.
model = torchani.nn.Sequential(aev_computer, nn).to(device)

###############################################################################
# Here we will use Adam with weight decay for the weights and Stochastic Gradient
# Descent for biases.

AdamW = torch.optim.AdamW([
    # H networks
    {'params': [H_network[0].weight]},
    {'params': [H_network[2].weight], 'weight_decay': 0.00001},
    {'params': [H_network[4].weight], 'weight_decay': 0.000001},
    {'params': [H_network[6].weight]},
    # C networks
    {'params': [C_network[0].weight]},
    {'params': [C_network[2].weight], 'weight_decay': 0.00001},
    {'params': [C_network[4].weight], 'weight_decay': 0.000001},
    {'params': [C_network[6].weight]},
])

SGD = torch.optim.SGD([
    # H networks
    {'params': [H_network[0].bias]},
    {'params': [H_network[2].bias]},
    {'params': [H_network[4].bias]},
    {'params': [H_network[6].bias]},
    # C networks
    {'params': [C_network[0].bias]},
    {'params': [C_network[2].bias]},
    {'params': [C_network[4].bias]},
    {'params': [C_network[6].bias]},
], lr=1e-3)

AdamW_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(AdamW, factor=0.5, patience=100, threshold=0)
SGD_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(SGD, factor=0.5, patience=100, threshold=0)

###############################################################################
# This part of the code is also the same
latest_checkpoint = 'force-training-latest.pt'

###############################################################################
# Resume training from previously saved checkpoints:
if os.path.isfile(latest_checkpoint):
    checkpoint = torch.load(latest_checkpoint)
    nn.load_state_dict(checkpoint['nn'])
    AdamW.load_state_dict(checkpoint['AdamW'])
    SGD.load_state_dict(checkpoint['SGD'])
    AdamW_scheduler.load_state_dict(checkpoint['AdamW_scheduler'])
    SGD_scheduler.load_state_dict(checkpoint['SGD_scheduler'])

###############################################################################
# During training, we need to validate on validation set and if validation error
# is better than the best, then save the new best model to a checkpoint


def validate():
    # run validation
    mse_sum = torch.nn.MSELoss(reduction='sum')
    total_mse = 0.0
    count = 0
    total_msef =0.0
    
    model.train(False)
    with torch.no_grad():
        for properties in validation:
            species = properties['species'].to(device)
            coordinates = properties['coordinates'].to(device).float()
            true_energies = properties['energies'].to(device).float()
            true_forces = properties['forces'].to(device).float()            
            cell = properties['cell'].to(device).float()            
            _, predicted_energies = model((species, coordinates),cell,pbc)
            #forces = -torch.autograd.grad(predicted_energies.sum(), coordinates, create_graph=True, retain_graph=True)[0]

            total_mse += mse_sum(predicted_energies, true_energies).item()
            #total_msef += mse_sum(true_forces, forces).sum(dim=(1, 2)).item()            
            count += predicted_energies.shape[0]

            
    model.train(True)
    return hartree2kcalmol(math.sqrt(total_mse / count)),hartree2kcalmol(math.sqrt(total_msef / count))


###############################################################################
# We will also use TensorBoard to visualize our training process
tensorboard = torch.utils.tensorboard.SummaryWriter()

###############################################################################
# In the training loop, we need to compute force, and loss for forces
mse = torch.nn.MSELoss(reduction='none')

print("training starting from epoch", AdamW_scheduler.last_epoch + 1)
# We only train 3 epoches here in able to generate the docs quickly.
# Real training should take much more than 3 epoches.
max_epochs = 300
early_stopping_learning_rate = 1.0E-5
force_coefficient = 0.1  # controls the importance of energy loss vs force loss
best_model_checkpoint = 'force-training-best.pt'

for _ in range(AdamW_scheduler.last_epoch + 1, max_epochs):
    rmse,rmse_f = validate()

    
    print('RMSE:', rmse, 'at epoch', AdamW_scheduler.last_epoch + 1)

    learning_rate = AdamW.param_groups[0]['lr']

    if learning_rate < early_stopping_learning_rate:
        break

    # checkpoint
    if AdamW_scheduler.is_better(rmse, AdamW_scheduler.best):
        torch.save(nn.state_dict(), best_model_checkpoint)

    AdamW_scheduler.step(rmse)
    SGD_scheduler.step(rmse)

    tensorboard.add_scalar('validation_rmse', rmse, AdamW_scheduler.last_epoch)
    tensorboard.add_scalar('best_validation_rmse', AdamW_scheduler.best, AdamW_scheduler.last_epoch)
    tensorboard.add_scalar('learning_rate', learning_rate, AdamW_scheduler.last_epoch)


    # Besides being stored in x, species and coordinates are also stored in y.
    # So here, for simplicity, we just ignore the x and use y for everything.
    for i, properties in tqdm.tqdm(
        enumerate(training),
        total=len(training),
        desc="epoch {}".format(AdamW_scheduler.last_epoch)
    ):
        species = properties['species'].to(device)
        coordinates = properties['coordinates'].to(device).float().requires_grad_(True)
        true_energies = properties['energies'].to(device).float()
        true_forces = properties['forces'].to(device).float()
        cell = properties['cell'].to(device).float()        
        num_atoms = (species >= 0).sum(dim=1, dtype=true_energies.dtype)
        _, predicted_energies = model((species, coordinates),cell,pbc)

        # We can use torch.autograd.grad to compute force. Remember to
        # create graph so that the loss of the force can contribute to
        # the gradient of parameters, and also to retain graph so that
        # we can backward through it a second time when computing gradient
        # w.r.t. parameters.
        forces = -torch.autograd.grad(predicted_energies.sum(), coordinates, create_graph=True, retain_graph=True)[0]

        # Now the total loss has two parts, energy loss and force loss
        energy_loss = (mse(predicted_energies, true_energies) / num_atoms.sqrt()).mean()
        force_loss = (mse(true_forces, forces).sum(dim=(1, 2)) / num_atoms).mean()
        loss = energy_loss + force_coefficient * force_loss

        AdamW.zero_grad()
        SGD.zero_grad()
        loss.backward()
        AdamW.step()
        SGD.step()

        # write current batch loss to TensorBoard
        tensorboard.add_scalar('Energy_loss',energy_loss,AdamW_scheduler.last_epoch)
        tensorboard.add_scalar('Force_loss',force_loss,AdamW_scheduler.last_epoch)                
        tensorboard.add_scalar('batch_loss',loss, AdamW_scheduler.last_epoch * len(training) + i)

    torch.save({
        'nn': nn.state_dict(),
        'AdamW': AdamW.state_dict(),
        'SGD': SGD.state_dict(),
        'AdamW_scheduler': AdamW_scheduler.state_dict(),
        'SGD_scheduler': SGD_scheduler.state_dict(),
    }, latest_checkpoint)
