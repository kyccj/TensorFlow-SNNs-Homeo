'''
    Configuration for SNN direct training

'''

# GPU setting
import os
#os.environ['NCCL_P2P_DISABLE']='1'
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"]="0,2"
#os.environ["CUDA_VISIBLE_DEVICES"]="4,7"
os.environ["CUDA_VISIBLE_DEVICES"]="0"
#os.environ["CUDA_VISIBLE_DEVICES"]="0,1,2,3,4,5,6,7"
#os.environ["CUDA_VISIBLE_DEVICES"]="0,1,2,3"
#os.environ["CUDA_VISIBLE_DEVICES"]="0,4"
#os.environ["CUDA_VISIBLE_DEVICES"]="2,3,4,5,6,7"
#os.environ["CUDA_VISIBLE_DEVICES"]="2,3,6,7"
#os.environ["CUDA_VISIBLE_DEVICES"]="4,5,6,7"


#
from config import config
conf = config.flags

#
#conf.debug_mode = True
#conf.verbose_snn_train = True


#
#conf.mode='inference'
##conf.batch_size_inf=100
#conf.batch_size=400
#conf.batch_size=200
#conf.batch_size=300
#conf.batch_size=180
#conf.batch_size=120
#conf.time_step=2
#conf.name_model_load='./models/VGG16_AP_CIFAR100/ep-300_bat-100_opt-SGD_lr-STEP-1E-01_lmb-1E-04_sc_cm_ts-4_nc-R-R_nr-z'


#
#conf.learning_rate = 0.01

#
#conf.train_epoch = 120
#conf.step_decay_epoch = 40
#conf.train_epoch = 10
#conf.train_epoch = 10
#conf.num_train_data = 10000

#conf.model='ResNet20'
#conf.model='ResNet32'

#conf.dataset='CIFAR100'
#conf.dataset='ImageNet'
#conf.dataset='CIFAR10_DVS'


#conf.pooling_vgg = 'avg'

conf.nn_mode = 'SNN'
#conf.nn_mode = 'ANN'

conf.n_reset_type = 'reset_by_sub'
#conf.n_reset_type = 'reset_to_zero'


conf.vth_rand_static = False
conf.vrest = 0.0
#conf.vrest_rand_static = False
#conf.vrest_rand_static = True

#conf.adaptive_vth = False
#conf.adaptive_vth = True
conf.adaptive_vth_scale = 1.2

#conf.use_bn=False

#conf.n_init_vth = 0.3

conf.leak_const_init = 0.9
#conf.leak_const_train = True


#
conf.reg_spike_out_sc=True
conf.reg_spike_out=True
conf.reg_spike_out_const=0.01
conf.reg_spike_out_alpha=0.1

#
conf.reg_psp=True
conf.reg_psp_const=1E-7
conf.reg_psp_eps=1E-2
conf.reg_psp_min=True



#
#conf.grad_clipnorm = 3.0
#conf.grad_clipnorm = 1.0

#
#conf.en_stdp_pathway = True
conf.stdp_pathway_weight = 0.1

#
config.set()