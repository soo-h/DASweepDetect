import tensorflow as tf

@tf.custom_gradient
def gradient_reversal(x,alpha):
    def grad(dy):
        return -dy * alpha, None
        #return -dy * alpha
    return x, grad


def loss_domain(label,domain):
    domain = tf.clip_by_value(domain,0.001,0.999)
    p2 = 1. - domain
    loss = -label * tf.math.log(domain) - (1-label) * tf.math.log(p2)
    return loss

def early_stop(threshold=5):
    ##　早停，验证集精确度ｎ代不上升－－－－＞　返回True
    ##　参数：忍受代数；输入数据： int、float
    acc_before = 0
    count = 0
    iter_count = 0
    best_iter = 0
    #threshold = threshold
    def compaer_loss(acc_current):
        nonlocal acc_before,count,iter_count,best_iter
        iter_count += 1
        if acc_current >= acc_before:
            acc_before = acc_current
            best_iter = iter_count 
            count = 0
        else:
            count += 1
        print(count)
        if count >= threshold:
            print(f'break,val acc not improve {threshold} times!!!')
            return True,best_iter
        
        return False,best_iter
    
    return compaer_loss