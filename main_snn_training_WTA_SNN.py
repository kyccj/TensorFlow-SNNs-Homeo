
#
# configuration
from config_snn_training_WTA_SNN import config

#
import tensorflow as tf

# snn library
import lib_snn

#
import datasets
import callbacks

########################################
# configuration
########################################
dist_strategy = lib_snn.utils.set_gpu()


################
# name set
################
#
filepath_save, filepath_load, config_name = lib_snn.utils.set_file_path()

########################################
# load dataset
########################################
train_ds, valid_ds, test_ds, train_ds_num, valid_ds_num, test_ds_num, num_class, train_steps_per_epoch = \
    datasets.datasets.load()
    #datasets.datasets_bck_eventdata.load()


#
with dist_strategy.scope():

    ########################################
    # build model
    ########################################
    #data_batch = valid_ds.take(1)
    #model = lib_snn.model_builder.model_builder(num_class,train_steps_per_epoch)
    model = lib_snn.model_builder.model_builder(num_class,train_steps_per_epoch,valid_ds)

    ########################################
    # load model
    ########################################
    if config.load_model:
        model.load_weights(config.load_weight)

    ################
    # Callbacks
    ################
    callbacks_train, callbacks_test = \
        callbacks.callbacks_snn_train(model,train_ds_num,valid_ds,test_ds_num)

    #if True:
    if False:
        if config.train:
            print('Train mode')

            model.summary()
            #train_steps_per_epoch = train_ds_num/batch_size
            train_epoch = config.flags.train_epoch
            init_epoch = config.init_epoch
            train_histories = model.fit(train_ds, epochs=train_epoch, steps_per_epoch=train_steps_per_epoch,
                                        initial_epoch=init_epoch, validation_data=valid_ds, callbacks=callbacks_train)
        else:
            print('Test mode')

            result = model.evaluate(test_ds, callbacks=callbacks_test)

    # plot kernel
    if False:
        from lib_snn.sim import glb_plot_kernel
        for layer in model.layers:
            if hasattr(layer,'kernel'):
                lib_snn.utils.plot_hist(glb_plot_kernel,layer.kernel,100,norm_fit=True)
                name = layer.name
                mean = tf.reduce_mean(layer.kernel)
                std = tf.math.reduce_std(layer.kernel)

                print('{:} - mean: {:e}, std: {:e} '.format(layer.name,mean,std))




    en_analysis = False
    #en_analysis = True

    if en_analysis:
        # analysis
        import tensorflow as tf
        import numpy as np
        import pandas as pd
        from absl import flags
        conf = flags.FLAGS

        l_n = []
        l_sc = []
        for layer in model.layers_w_neuron:
            print(layer.name)
            l_n.append(layer.name)
            spike_count = layer.act.spike_count_int.numpy()
            #hist = tf.histogram_fixed_width(spike_count, [0, conf.time_step+1], nbins=conf.time_step+1)
            hist,_ = np.histogram(spike_count,bins=conf.time_step+1)
            print(hist)
            l_sc.append(hist)

        a_sc = np.vstack(l_sc).T

        df = pd.DataFrame({'name':l_n,'0':a_sc[0],'1':a_sc[1],'2':a_sc[2],'3':a_sc[3],'4':a_sc[4]})


        df.to_excel(config.config_name+".xlsx")


    #
    # visualization - activation
    #
    #if False:
    if True:
        #psp_mode = True
        psp_mode = False
        import keras
        import matplotlib.pyplot as plt

        # get a image
        imgs_labs, = test_ds.take(1)
        imgs = imgs_labs[0]
        img = imgs[0]
        img = tf.expand_dims(img, axis=0)


        layer_outputs = []
        layer_names = []
        for layer in model.layers:
            if isinstance(layer,lib_snn.activations.Activation):
                if psp_mode:
                    layer_outputs.append(layer.input)
                else:
                    layer_outputs.append(layer.output)
                layer_names.append(layer.name)

        act_model=keras.Model(inputs=model.input,outputs=layer_outputs)

        act = act_model.predict(img)

        plt.matshow(act[1][0,:,:,3])



    # visualization - spike count
    #if False:
    if True:
        result = model.evaluate(test_ds.take(1), callbacks=callbacks_test)
        sc = []
        for layer in model.layers_w_neuron:
            if isinstance(layer.act,lib_snn.neurons.Neuron):
                sc.append(layer.act.spike_count_int)




    # XAI - integrated gradients
    # batch size should be m_steps+1
    if False:
    #if True:

        import matplotlib.pyplot as plt

        [imgs, labels], = test_ds.take(1)

        #sample_idx=6   # horse -> good
        sample_idx=10   # horse -> good example
        #sample_idx=30   # ? -> good
        #sample_idx=40   # -> good
        #sample_idx=50   # -> good


        img = imgs[sample_idx]
        label = labels[sample_idx]

        baseline = tf.random.uniform(shape=img.shape,minval=0,maxval=1)


        m_steps = 99
        #m_steps = 50
        #label_decoded=386
        label_decoded = tf.argmax(label)

        #image_processed = tf.expand_dims(img,axis=0)
        img_exp = tf.expand_dims(img,axis=0)
        ig_attribution = lib_snn.xai.integrated_gradients(model=model,
                                                          baseline=baseline,
                                                          images=img,
                                                          target_class_idxs=label_decoded,
                                                          m_steps=m_steps)

        #_ = lib_snn.xai.plot_image_attributions(baseline,img_processed,ig_attribution)


        # 5. Get the gradients of the last layer for the predicted label
        grads = lib_snn.integrated_gradients.get_gradients(model,img_exp,top_pred_idx=label_decoded)

        #
        vis = lib_snn.integrated_gradients.GradVisualizer()

        vis.visualize(
            image=img,
            gradients=grads[0].numpy(),
            integrated_gradients=ig_attribution.numpy(),
            clip_above_percentile=99,
            clip_below_percentile=0
        )


        vis.visualize(
            image=img,
            gradients=grads[0].numpy(),
            integrated_gradients=ig_attribution.numpy(),
            clip_above_percentile=95,
            clip_below_percentile=28,
            morphological_cleanup=True,
            outlines=True
        )

        plt.show()
