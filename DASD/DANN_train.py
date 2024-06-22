import os
import sys
import subprocess

import numpy as np
import tensorflow as tf
#from tensorflow.keras.utils import to_categorical
from keras.utils import np_utilsa
import matplotlib.pyplot as plt

from util.pretreatment import max_minNorm
from util.DANN_ import feature_extracter, classifier, Discriminator, DANN
from util.loss import gradient_reversal, loss_domain, early_stop
from util.train_utils import parse_model_name, get_target_data_paths

def sampled_target_data(target_data, extraction_number):
    factor = 2
    extraction_number_every_file = int(factor * extraction_number // len(target_data))

    def data_generator():
        for file in target_data:
            with open(file, 'rb') as f:
                data = np.load(f)
                if data.shape[0] < extraction_number_every_file:
                    yield data
                else:
                    idx = np.random.choice(data.shape[0], extraction_number_every_file, replace=False)
                    yield data[idx]

    target = np.concatenate(list(data_generator()))
    if target.shape[0] < extraction_number:
        print('Warning: real feature map too less!!!')
    return target


def train(epoch,model_name, source_dataset, target_dataset, val_dataset ,lamda=1,stop=5):
    """
    Train a DANN model with early stopping.
    
    Args:
        epoch (int): Maximum number of epochs to train.
        model_name (str): Name for saving the model.
        source_dataset (tf.data.Dataset): Source domain dataset.
        target_dataset (tf.data.Dataset): Target domain dataset.
        val_dataset (tf.data.Dataset): Validation dataset.
        lamda (float): Alignment loss hyperparameter.
        stop (int): Early stopping parameter.
        
    Returns:
        tuple: Name of the best model if early stopping occurs, otherwise 0 and the log filename.
    """
    model = DANN(classify=5)
    log = f'{model_name}.log'
    f = open(log, 'w')
    DANN_name = model_name
    lamda = lamda
    
    lr = 1e-2
    optimizer = tf.keras.optimizers.SGD(lr)
    loss_class = tf.keras.losses.categorical_crossentropy

    @tf.function
    def train_step(x_s, x_t, model, alpha, lamda, train_accuracy):
        source_X, class_label = x_s
        class_label = tf.cast(class_label, dtype='float32')
        source_domain_label = tf.zeros(len(class_label))
        source_domain_label = tf.cast(source_domain_label, dtype='float32')
        source_X = tf.cast(source_X, tf.float32)

        target_X, _ = x_t
        target_domain_label = tf.cast(_, dtype='float32')

        with tf.GradientTape() as tape:
            class_output, domain_output1 = model(source_X, alpha=alpha)
            _, domain_output2 = model(target_X, alpha=alpha)
            err_s_label = tf.reduce_mean(loss_class(class_label, class_output))
            err_s_domain = tf.reduce_mean(loss_domain(source_domain_label, domain_output1))
            err_t_domain = tf.reduce_mean(loss_domain(target_domain_label, domain_output2))

            total_loss = err_s_label + lamda * (err_s_domain + err_t_domain)

        gradients = tape.gradient(total_loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))

        train_accuracy.update_state(class_label, class_output)

        return total_loss, err_s_label, err_s_domain, err_t_domain

    @tf.function
    def test_step(inputs, model, alpha, test_loss_container, test_accuracy):
        loss_class = tf.keras.losses.categorical_crossentropy

        # model = model
        images, labels = inputs

        images = tf.cast(images, tf.float32)
        class_output, _ = model(images, alpha)
        t_loss = tf.reduce_mean(loss_class(labels, class_output))

        test_loss_container.update_state(t_loss)
        test_accuracy.update_state(labels, class_output)


    # early stop
    stop_monitor = early_stop(stop)
    train_accuracy = tf.keras.metrics.CategoricalAccuracy(name='train_accuracy')
    train_loss_container = tf.keras.metrics.Mean(name='train_loss')
    domain_loss_container = tf.keras.metrics.Mean(name='trans_loss')

    test_loss_container = tf.keras.metrics.Mean(name='test_loss')
    test_accuracy = tf.keras.metrics.CategoricalAccuracy(name='test_accuracy')

    EPOCHS = epoch

    First = True
    print('train Begaining!!!')
    for epoch in range(EPOCHS):

        total_Loss = 0.0
        num_batches = 0

        data_source_iter = iter(source_dataset)
        data_target_iter = iter(target_dataset)

        i = 0
        while i < n_step:
            p = float(i + epoch * n_step) / EPOCHS / n_step
            alpha = tf.constant(2. / (1. + np.exp(-10 * p)) - 1, dtype='float32')

            x_s = data_source_iter.get_next()
            x_t = data_target_iter.get_next()

            total_loss, class_loss, err_s_domain, err_t_domain = train_step(x_s, x_t, model, alpha, lamda, train_accuracy)

            domain_loss = err_s_domain + err_t_domain
            domain_loss_container.update_state(domain_loss)
            train_loss_container.update_state(class_loss)

            total_Loss += total_loss
            num_batches += 1
            i += 1

            if First:
                if epoch == 0:
                    batch_log = 'epoch: %d, [iter: %d / all %d], err_s_label: %f, err_s_domain: %f, err_t_domain: %f' \
                                % (epoch, i, n_step, class_loss, err_s_domain, err_t_domain)
                    print(batch_log)
                    f.write(f'{batch_log}\n')
                else:
                    First = False

        train_loss_total = total_Loss / num_batches

        for x in val_dataset:
            test_step(x, model, alpha, test_loss_container, test_accuracy)

        template = (
            "Epoch {}, TotalLoss: {}, Loss_Class: {}, Loss_Domain:{},Accuracy: {} \n validSet: Loss1: {},Accuracy_val: {}")
        epoch_log = template.format(epoch + 1, train_loss_total, train_loss_container.result(),\
                                    domain_loss_container.result(), train_accuracy.result() * 100, \
                                    test_loss_container.result(), test_accuracy.result() * 100)

        print(epoch_log)
        f.write(epoch_log + '\n')

        modelName = f'{model_name}_epoch{epoch}'
        tf.keras.models.save_model(model, modelName)

        stop, best_iter = stop_monitor(test_accuracy.result())
        if stop == True:
            best_model = f"{DANN_name}_epoch{best_iter - 1}"
            f.write(f'best model:  {best_model}')
            f.close()

            return best_model,log

        train_accuracy.reset_states()
        train_loss_container.reset_states()
        domain_loss_container.reset_states()

        test_loss_container.reset_states()
        test_accuracy.reset_states()

    f.close()
    return 0,log


def read_log(log_name):
    with open(log_name, 'r') as log:
        train_log = []
        valid_log = []
        for line in log:
            if line.startswith('Epoch'):
                train_log.append(line)
            if line.startswith(' validSet'):
                valid_log.append(line)
            if line.startswith('best'):
                print(line)

    train_acc = [float(line.strip().split(',')[-1].split(':')[1]) for line in train_log]
    train_loss = [float(line.strip().split(',')[2].split(':')[1]) for line in train_log]
    valid_acc = [float(line.strip().split(',')[1].split(':')[1].split('/n')[0]) for line in valid_log]
    valid_loss = [float(line.strip().split(',')[0].split(':')[-1]) for line in valid_log]
    return train_acc,train_loss,valid_acc,valid_loss

def plot_train_log(ensemble_log, opt=None):
    fig, ax = plt.subplots(2, 2, figsize=(20, 6))

    for log in ensemble_log:
        t_acc, t_loss, v_acc, v_loss = read_log(log)

        epochs = range(len(t_acc))
        ax[0][0].plot(epochs, t_acc)
        ax[0][1].plot(epochs, v_acc)
        ax[1][0].plot(epochs, t_loss)
        ax[1][1].plot(epochs, v_loss)

    ax[0][0].legend(loc='lower right')
    ax[0][0].set_title('Training accuracy')

    ax[0][1].legend(loc='lower right')
    ax[0][1].set_title('validation accuracy')

    ax[1][0].legend(loc='lower right')
    ax[1][0].set_title('Training loss')

    ax[1][1].legend(loc='lower right')
    ax[1][1].set_title('validation loss')
    if opt:
        plt.savefig(f'{opt}.pdf', format="PDF")
    return 0

def ensemble_train(epoch, model_dir_path, model_name_prefix, source_dataset, target_dataset, val_dataset , M=M, save=save):
    epoch = epoch
    best_model_list = []

    ensemble_dir = f"{model_dir_path}{model_name_prefix}_ensemble"
    os.makedirs(ensemble_dir,exist_ok=True)

    for i in range(M):
        model_dir = f"{model_dir_path}{model_name_prefix}_{i}"
        os.makedirs(model_dir, exist_ok=True)

        model_name = f"{model_dir}/{model_name_prefix}_{i}"# "model_name_prefix/"
        best_model,train_log = train(epoch, model_name, source_dataset, target_dataset, val_dataset, lamda=1, stop=5)

        if not best_model:
            log_name = f"{model_name}.log"
            train_acc, train_loss, valid_acc, valid_loss = read_log(log_name)
            best_iter = np.argmax(valid_acc)
            best_model = f"{model_name}_epoch{best_iter - 1}"

        best_model_list.append(best_model)

        # move
        cmd = f"mv {best_model} {train_log} {ensemble_dir}"
        subprocess.call(cmd, shell=True)
        # clean
        if not save:
            cmd = "rm -rf {model_dir}"
            subprocess.call(cmd, shell=True)

    return ensemble_dir


if __name__ == "__main__":
    train_path, train_labels_path, val_path, val_labels_path, test_path, test_labels_path, target_data_path, M, save, model_name = sys.argv[1:11]
    save = bool(save)
    M = int(M)

    model_dir_path, model_name_prefix = parse_model_name(model_name)

    staNum = 40
    BATCH_SIZE = 32
    EPOCHS = 50
    num_classes = 5

    # data preprocess
    dataSet_train = max_minNorm(np.load(train_path))
    dataSet_val = max_minNorm(np.load(val_path))
    dataSet_test = max_minNorm(np.load(test_path))
    # label one-hot encoding
    y = np_utils.to_categorical(np.load(train_labels_path), num_classes)
    y_val = np_utils.to_categorical(np.load(val_labels_path), num_classes)
    y_test = np_utils.to_categorical(np.load(test_labels_path), num_classes)

    # get target domain data
    target_data = get_target_data_paths(target_data_path)

    target_data = sampled_target_data(target_data, dataSet_train.shape[0])
    target_data[np.isnan(target_data)] = 0
    # preprocess
    target_data = max_minNorm(target_data)
    # check training data
    if not (staNum == target_data.shape[1] == dataSet_train.shape[1] == dataSet_val.shape[1] == dataSet_test.shape[1]):
        raise Exception("Error: shape of input data unequal ,please check all input data!")

    BUFFER_SIZE_SOURCE = len(dataSet_train)
    BUFFER_SIZE_TARGET = len(target_data)
    BUFFER_SIZE_VALID = len(dataSet_val)

    n_step = np.min([BUFFER_SIZE_TARGET, BUFFER_SIZE_SOURCE]) // BATCH_SIZE

    source_dataset = tf.data.Dataset.from_tensor_slices((dataSet_train, y)).shuffle(BUFFER_SIZE_SOURCE).batch(BATCH_SIZE)
    target_dataset = tf.data.Dataset.from_tensor_slices((target_data, np.repeat(1., len(target_data)))).shuffle(
        BUFFER_SIZE_TARGET).batch(BATCH_SIZE).repeat()
    val_dataset = tf.data.Dataset.from_tensor_slices((dataSet_val, y_val)).shuffle(BUFFER_SIZE_VALID).batch(BATCH_SIZE)

    print('data read complete!!!')

    ensemble_dir = ensemble_train(EPOCHS, model_dir_path, model_name_prefix, source_dataset, target_dataset, val_dataset , M=M, save=save)
    ensemble_log = [f'{ensemble_dir}/{name}' for name in os.listdir(ensemble_dir) if name.endswith('log')]
    plot_train_log(ensemble_log, opt=f"{model_dir_path}ensemble_training_plot")
