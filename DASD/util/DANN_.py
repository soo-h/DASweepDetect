import tensorflow as tf
from loss import gradient_reversal,loss_domain

class feature_extracter(tf.keras.layers.Layer):
    ## 输入的每个sample为二维张量
    def __init__(self):
        super().__init__()
        self.conv_1_1 = tf.keras.layers.Conv1D(512,kernel_size=1,padding='valid',activation='relu')
        #tf.transpose(conv_1_1,[0,2,1])
        self.conv_1_2 = tf.keras.layers.Conv1D(256,kernel_size=1,padding='valid',activation='relu')
        
        self.conv_2_1 = tf.keras.layers.Conv2D(128,kernel_size=1,strides=1,padding='same',activation='relu')
        self.conv_2_2 = tf.keras.layers.Conv2D(256,kernel_size=(3,1),strides=2,padding='same',activation='relu')
        self.conv_2_3 = tf.keras.layers.Conv2D(128,kernel_size=1,strides=1,padding='same',activation='relu')
        
        self.conv_3_1 = tf.keras.layers.Conv2D(64,kernel_size=1,strides=1,padding='same',activation='relu')
        self.conv_3_2 = tf.keras.layers.Conv2D(128,kernel_size=(3,1),strides=2,padding='same',activation='relu')
        self.conv_3_3 = tf.keras.layers.Conv2D(64,kernel_size=(2,1),strides=1,padding='same',activation='relu')
        
 #       self.conv_4_1 = tf.keras.layers.Conv2D(64,kernel_size=(3,1),strides=2,padding='same',activation='relu')
        
  #      self.conv_5_1 = tf.keras.layers.Conv2D(32,kernel_size=(2,1),strides=1,padding='same',activation='relu')

        self.conv1 = tf.keras.layers.Flatten()
    
    def call(self,inputs):
        _,self.dim1,self.dim2 = inputs.shape
        x = tf.reshape(inputs,[-1,self.dim1,self.dim2])
        x = self.conv_1_1(x)
        x = tf.transpose(x,[0,2,1])
        x = self.conv_1_2(x)
        x = tf.expand_dims(x,axis=1)
        
        x = self.conv_2_1(x)
        x = self.conv_2_2(x)
        x = self.conv_2_3(x)
        
        x = self.conv_3_1(x)
        x = self.conv_3_2(x)
        x = self.conv_3_3(x)
        
   #     x = self.conv_4_1(x)
    #    x = self.conv_5_1(x)
        x = self.conv1(x)
        return x


class classifier(tf.keras.layers.Layer):
    ## 输入为flattern层输出的结果
    def __init__(self,classify):
        super().__init__()
        self.dense1 = tf.keras.layers.Dense(256)
        self.bn1 = tf.keras.layers.BatchNormalization()#注释
        self.relu1 = tf.keras.layers.ReLU()
        self.dropout = tf.keras.layers.Dropout(0.25)
        self.dense2 = tf.keras.layers.Dense(256)
       # self.bn2 = tf.keras.layers.BatchNormalization()
        self.dropout2 = tf.keras.layers.Dropout(0.05)
        self.dense3 = tf.keras.layers.Dense(128)
        self.relu2 = tf.keras.layers.ReLU()
        self.dense4 = tf.keras.layers.Dense(classify,activation='softmax')
        #self.out = tf.nn.log_softmax(axis=1)
    
    def call(self,inputs):
            
        x = self.dense1(inputs)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.dropout(x)  
        x = self.dense2(x)
        x = self.dropout2(x)
        x = self.dense3(x)
        x = self.relu2(x)
        x = self.dense4(x)

        return x


class Discriminator(tf.keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.dense1 = tf.keras.layers.Dense(256)
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.relu1 = tf.keras.layers.ReLU()
        self.dense2 = tf.keras.layers.Dense(1,activation='sigmoid')
    def call(self,inputs):
        x = self.dense1(inputs)
        x = self.bn1(x)
        x = self.relu1(x)
        
        x = self.dense2(x)
        #x = tf.math.log(x)
        
        return x


class DANN(tf.keras.Model):
    def __init__(self,classify):
        super().__init__()
        self.feature = feature_extracter()
        self.classifier = classifier(classify)
        self.Discriminator = Discriminator()
    
    def call(self,inputs,alpha):
        feature = self.feature(inputs)
        
        reverse_feature = gradient_reversal(feature,alpha)
        
        class_output = self.classifier(feature)
 
        ## 梯度反传
        discrim_output = self.Discriminator(reverse_feature)
        
        return class_output,discrim_output