from __future__ import division
from __future__ import print_function
from time import gmtime, strftime

import time
import sys
import os
from pylab import *
from scipy import sparse
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.cross_validation import StratifiedKFold

# Given a set of ratings, 2 matrix factors that include one or more
# trainable variables, and a regularizer, uses gradient descent toextract_rating_info
# learn the best values of the trainable variables.
def mf(ratings_train, W, H, regularizer, mean_rating, max_iter, lr = 0.01, decay_lr = False, log_summaries = False):
    # Extract info from training and validation data
    rating_values_tr, num_ratings_tr, user_indices_tr,item_indices_tr = extract_rating_info(ratings_train)

    # Multiply the factors to get our result as a dense matrix
    user_sparse = tf.gather(W,user_indices_tr,name = "extract_user_vectors")
    print('shape of W is '+str(W.shape))
    item_sparse = tf.gather(H,item_indices_tr,axis = 1,name = "extract_item_vectors")
    print('shape of H is '+str(H.shape))
    result_values_tr = tf.einsum('ij,ij->i',user_sparse,tf.transpose(item_sparse))

    diff_op = tf.subtract(tf.add(result_values_tr, mean_rating, name="add_mean"), rating_values_tr, name="raw_training_error")

    with tf.name_scope("training_cost") as scope:
        base_cost = tf.reduce_sum(tf.square(diff_op, name="squared_difference"), name="sum_squared_error")

        cost = tf.div(tf.add(base_cost, regularizer), num_ratings_tr * 2, name="average_error")

    with tf.name_scope("train") as scope:
        if decay_lr:
            # Use an exponentially decaying learning rate.
            global_step = tf.Variable(0, trainable=False)
            learning_rate = tf.train.exponential_decay(lr, global_step, 10000, 0.96, staircase=True)
            optimizer = tf.train.GradientDescentOptimizer(learning_rate)
            # Passing global_step to minimize() will increment it at each step 
            # so that the learning rate will be decayed at the specified 
            # intervals.
            train_step = optimizer.minimize(cost, global_step=global_step)
        else:
            optimizer = tf.train.AdamOptimizer(lr)
            train_step = optimizer.minimize(cost)

    with tf.name_scope("training_rmse") as scope:
      rmse_tr = tf.sqrt(tf.reduce_sum(tf.square(diff_op)) / num_ratings_tr)

    # Create a TensorFlow session and initialize variables.
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    if log_summaries:
        # Make sure summaries get written to the logs.
        accuracy_tr_summary =  tf.summary.scalar("cost", cost)
        summary_op = tf.summary.merge_all()
        writer = tf.summary.FileWriter("/tmp/recommender_logs", sess.graph_def)
    # Keep track of cost difference.
    last_cost = 0
    diff = 1
    # Run the graph and see how we're doing on every 1000th iteration.
    for i in range(max_iter):
        print ('in mf i count = '+str(i))
        if i > 0 and i % 1000 == 0:
            if diff < 0.000001:
                print("Converged at iteration %s" % (i))
                break;
            res = sess.run([rmse_tr, cost])
            acc_tr = res[0]
            cost_ev = res[1]
            print("Training RMSE at step %s: %s" % (i, acc_tr))
            diff = abs(cost_ev - last_cost)
            last_cost = cost_ev
        else:
            
            res = sess.run([train_step,summary_op] )
            summary_str = res[1]
            writer.add_summary(summary_str,i)

    finalTrain = rmse_tr.eval(session=sess)
    finalW = W.eval(session=sess)
    finalH = H.eval(session=sess)
    sess.close()
    return finalTrain, finalW, finalH

def mf2(ratings_train, W,access_his, H, regularizer,t_emb,t_vec, Ma , mean_rating, max_iter, lr = 0.01, decay_lr = False, log_summaries = False):
    # Extract info from training and validation data
    rating_values_tr, num_ratings_tr, user_indices_tr,item_indices_tr = extract_rating_info(ratings_train)
    print ('shape of Ma = '+str(Ma.shape))
    print ('shape of H = '+str(H.shape))
    print ('shape of t_emb = '+str(t_emb.shape))

    # Multiply the factors to get our result as a dense matrix
    mod_h = tf.matmul(Ma,H)
    
    # Now we just want the values represented by the pairs of user and item
    # indices for which we had known ratings.
    user_sparse = tf.gather(W,user_indices_tr,name = "extract_user_vectors")
    user_sparse2 = tf.gather(access_his,user_indices_tr,name = "extract_user_access_vectors")
    print('shape of W is '+str(W.shape))
    item_sparse = tf.gather(mod_h,item_indices_tr,axis = 1,name = "extract_item_vectors")
    time_sparse = tf.gather(t_emb,item_indices_tr,name = "extract_event_time_vectors")
    print ('shape of item_sparse '+str(item_sparse.shape))
    print ('shape of time_sparse '+str(time_sparse.shape))
    time_effect_tr = tf.einsum('ij,ij->i',user_sparse,time_sparse)
    access_effect_tr = tf.einsum('ij,ij->i',tf.transpose(item_sparse),user_sparse2)
    total_effect_tr = tf.multiply(access_effect_tr,time_effect_tr)
    
    print('shape of H is '+str(H.shape))
    result_values_tr = tf.einsum('ij,ij->i',user_sparse,tf.transpose(item_sparse))
    result_values_tr = tf.multiply(result_values_tr,total_effect_tr)

    diff_op = tf.subtract(tf.add(result_values_tr, mean_rating, name="add_mean"), rating_values_tr, name="raw_training_error")

    with tf.name_scope("training_cost") as scope:
        base_cost = tf.reduce_sum(tf.square(diff_op, name="squared_difference"), name="sum_squared_error")

#        cost = tf.div(tf.add(base_cost, regularizer), num_ratings_tr * 2, name="average_error")
        cost = tf.div(base_cost, num_ratings_tr , name="average_error")

    with tf.name_scope("train") as scope:
        if decay_lr:
            # Use an exponentially decaying learning rate.
            global_step = tf.Variable(0, trainable=False)
            learning_rate = tf.train.exponential_decay(lr, global_step, 10000, 0.96, staircase=True)
            optimizer = tf.train.GradientDescentOptimizer(learning_rate)
            # Passing global_step to minimize() will increment it at each step 
            # so that the learning rate will be decayed at the specified 
            # intervals.
            train_step = optimizer.minimize(cost, global_step=global_step)
        else:
            optimizer = tf.train.AdamOptimizer(lr)
            train_step = optimizer.minimize(cost)

    with tf.name_scope("training_rmse") as scope:
      rmse_tr = tf.sqrt(tf.reduce_sum(tf.square(diff_op)) / num_ratings_tr)

    # Create a TensorFlow session and initialize variables.
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    if log_summaries:
        accuracy_tr_summary =  tf.summary.scalar("final_cost", cost)
        summary_op = tf.summary.merge_all()
        writer = tf.summary.FileWriter("/tmp/recommender_logs", sess.graph_def)
    # Keep track of cost difference.
    last_cost = 0
    diff = 1
    # Run the graph and see how we're doing on every 1000th iteration.
    for i in range(max_iter):
        print ('in mf i count = '+str(i))
        if i > 0 and i % 1000 == 0:
            if diff < 0.000001:
                print("Converged at iteration %s" % (i))
                break;
            res = sess.run([rmse_tr, cost])
            acc_tr = res[0]
            cost_ev = res[1]
            print("Training RMSE at step %s: %s" % (i, acc_tr))
            diff = abs(cost_ev - last_cost)
            last_cost = cost_ev
        else:
            res = sess.run([train_step,summary_op] )
            summary_str = res[1]
            writer.add_summary(summary_str,i)

            sess.run(train_step)

    finalTrain = rmse_tr.eval(session=sess)
    finalW = W.eval(session=sess)
    finalH = H.eval(session=sess)
    mat = Ma.eval(session=sess)
    T_result = t_emb.eval(session=sess)
    sess.close()
    return finalTrain,mat,T_result

def mf3(ratings_train, W, H, regularizer, FD, mean_rating, max_iter, lr = 0.01, decay_lr = False, log_summaries = False):
    # Extract info from training and validation data
    rating_values_tr, num_ratings_tr, user_indices_tr,item_indices_tr = extract_rating_info(ratings_train)

    # Multiply the factors to get our result as a dense matrix
    
    # Now we just want the values represented by the pairs of user and item
    # indices for which we had known ratings.
    user_sparse = tf.gather(W,user_indices_tr,name = "extract_user_vectors")
    print('shape of W is '+str(W.shape))
    item_sparse = tf.gather(H,item_indices_tr,axis = 1,name = "extract_item_vectors")
    print('shape of H is '+str(H.shape))
    result_values_tr = tf.einsum('ij,ij->i',user_sparse,tf.transpose(item_sparse))

    diff_op = tf.subtract(tf.add(result_values_tr, mean_rating, name="add_mean"), rating_values_tr, name="raw_training_error")

    with tf.name_scope("training_cost") as scope:
        base_cost = tf.reduce_sum(tf.square(diff_op, name="squared_difference"), name="sum_squared_error")

        cost = tf.div(tf.add(base_cost, regularizer), num_ratings_tr * 2, name="average_error")
#        cost = tf.div(base_cost, num_ratings_tr , name="average_error")

    with tf.name_scope("train") as scope:
        if decay_lr:
            # Use an exponentially decaying learning rate.
            global_step = tf.Variable(0, trainable=False)
            learning_rate = tf.train.exponential_decay(lr, global_step, 10000, 0.96, staircase=True)
            optimizer = tf.train.GradientDescentOptimizer(learning_rate)
            # Passing global_step to minimize() will increment it at each step 
            # so that the learning rate will be decayed at the specified 
            # intervals.
            train_step = optimizer.minimize(cost, global_step=global_step)
        else:
            optimizer = tf.train.AdamOptimizer(lr)
            train_step = optimizer.minimize(cost)

    with tf.name_scope("training_rmse") as scope:
      rmse_tr = tf.sqrt(tf.reduce_sum(tf.square(diff_op)) / num_ratings_tr)

    # Create a TensorFlow session and initialize variables.
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    if log_summaries:
        accuracy_tr_summary =  tf.summary.scalar("cost_with_features", cost)
        summary_op = tf.summary.merge_all()
        writer = tf.summary.FileWriter("/tmp/recommender_logs", sess.graph_def)
    # Keep track of cost difference.
    last_cost = 0
    diff = 1
    # Run the graph and see how we're doing on every 1000th iteration.
    for i in range(max_iter):
        print ('in mf i count = '+str(i))
        if i > 0 and i % 1000 == 0:
            if diff < 0.000001:
                print("Converged at iteration %s" % (i))
                break;
            res = sess.run([rmse_tr, cost])
            acc_tr = res[0]
            cost_ev = res[1]
            print("Training RMSE at step %s: %s" % (i, acc_tr))
            diff = abs(cost_ev - last_cost)
            last_cost = cost_ev
        else:
            res = sess.run([train_step,summary_op] )
            summary_str = res[1]
            writer.add_summary(summary_str,i)

            sess.run(train_step)

    finalTrain = rmse_tr.eval(session=sess)
    finalW = W.eval(session=sess)
    finalH = H.eval(session=sess)
    fd = FD.eval(session=sess)
    sess.close()
    return finalTrain, finalW, finalH,fd


# Extracts user indices, item indices, rating values and number
# of ratings from the ratings triplets.
def extract_rating_info(ratings):
    rating_values = np.array(ratings[:,2], dtype=float32)
    user_indices = ratings[:,0]
    item_indices = ratings[:,1]
#    print ('shape of indices = '+str(indices.shape))
    num_ratings = len(rating_values)
    return rating_values, num_ratings, user_indices,item_indices



# Learns factors of the given rank with specified regularization parameter.
def create_factors_without_biases(num_users, num_items, rank, lda):
    # Initialize the matrix factors from random normals with mean 0. W will
    # represent users and H will represent items.
    W = tf.Variable(tf.truncated_normal([num_users, rank], stddev=0.02, mean=0), name="users")
    H = tf.Variable(tf.truncated_normal([rank, num_items], stddev=0.02, mean=0), name="items")
    regularizer = tf.multiply(tf.add(tf.reduce_sum(tf.square(W)), tf.reduce_sum(tf.square(H))), lda, name="regularize")
    return W, H, regularizer

# Given previously learned user bias and item bias vectors, creates
# tensors to learn factors of the given rank (excluding the bias vectors)
# and a regularizer.
def create_factors_with_biases(user_bias, item_bias, rank, lda):
    num_users = user_bias.shape[0]
    num_items = item_bias.shape[1]
    # Initialize the matrix factors from random normals with mean 0. W will
    # represent users and H will represent items.
    W = tf.Variable(tf.truncated_normal([num_users, rank], stddev=0.02, mean=0), name="users")
    H = tf.Variable(tf.truncated_normal([rank, num_items], stddev=0.02, mean=0), name="items")

    # To the user matrix we add a bias column holding the bias of each user,
    # and another column of 1s to multiply the item bias by.
    W_plus_bias = tf.concat([W, tf.convert_to_tensor(user_bias, dtype=float32, name="user_bias"), tf.ones((num_users,1), dtype=float32, name="item_bias_ones")],1)
    # To the item matrix we add a row of 1s to multiply the user bias by, and
    # a bias row holding the bias of each item.
    H_plus_bias = tf.concat([H, tf.ones((1, num_items), name="user_bias_ones", dtype=float32), tf.convert_to_tensor(item_bias, dtype=float32, name="item_bias")],0)
    regularizer = tf.multiply(tf.add(tf.reduce_sum(tf.square(W)), tf.reduce_sum(tf.square(H))), lda, name="regularize")
    return W_plus_bias, H_plus_bias, regularizer



def create_factors_with_features(fixed_w,user_features,fixed_h,item_features,num_features,rank,lda):
    
    Feature_Vectors = tf.Variable(tf.truncated_normal([num_features, rank], stddev=0.02, mean=0), name="features")
    user_emb = tf.nn.embedding_lookup(Feature_Vectors,user_features,name = "user_features")
    user_context = tf.reduce_sum(user_emb,axis = 1, name = "user_context")
    
    item_emb = tf.nn.embedding_lookup(Feature_Vectors,item_features,name ="item_features")
    item_context = tf.reduce_sum(item_emb,axis = 1, name="item_context")

    W = tf.Variable(fixed_w,dtype = float32,name="users")
    W_with_context = tf.add(W,user_context,name = "users_with_context")

    H = tf.Variable(fixed_h,dtype = float32,name="items")
    H_with_context = tf.add(H,tf.transpose(item_context),name = "items_with_context")
    
#    W_plus_bias = tf.concat([W_with_context, tf.convert_to_tensor(user_bias, dtype=float32, name="user_bias"), tf.ones((num_users,1), dtype=float32, name="item_bias_ones")],1)
    # To the item matrix we add a row of 1s to multiply the user bias by, and
    # a bias row holding the bias of each item.
#    H_plus_bias = tf.concat([H_with_context, tf.ones((1, num_items), name="user_bias_ones", dtype=float32), tf.convert_to_tensor(item_bias, dtype=float32, name="item_bias")],0)

    regularizer = tf.multiply(tf.add(tf.reduce_sum(tf.square(W_with_context)), tf.reduce_sum(tf.square(H_with_context))), lda, name="regularize")
    return W_with_context, H_with_context, Feature_Vectors, regularizer
    
    
    
def create_factors_with_event_time_and_history(user_vec,access_his,item_vec,t_diff,num_t,lda,rank,M,T_VEC,count):
    num_users = user_vec.shape[0]
    num_items = item_vec.shape[1]    
    rank1 = user_vec.shape[1]

    rank3 = item_vec.shape[0]
    print ('shape of user_vec = '+str(user_vec.shape))
    print ('shape of item_vec = '+str(item_vec.shape))    
    if count ==0:
        coefmatrix = tf.Variable(tf.truncated_normal([rank1,rank3],stddev = 0.02,mean = 0),name = "final_coef")
        T_DIFF = tf.Variable(tf.truncated_normal([num_t,rank1],stddev = 0.02,mean = 0),name = "time_diff_vec")
    else:
        coefmatrix = tf.Variable(M,name = "final_coef")
        T_DIFF = tf.Variable(T_VEC,name = "time_diff_vec")
    AC = tf.convert_to_tensor(access_his,dtype = float32,name="access_history")
    
    print ("shape of T_DIF "+str(T_DIFF.shape))    
    print ("shape of t_diff "+str(t_diff.shape))    
    time_emb = tf.nn.embedding_lookup(T_DIFF,t_diff,name = "user_features")
    print ("shape of T_DIF "+str(time_emb.shape)+" in and_history")    

    W = tf.convert_to_tensor(user_vec,dtype = float32,name="users")

    print ('shape of item_vec'+str(item_vec.shape))
    print ('shape of coefmatrix'+str(coefmatrix.shape))

    H = tf.convert_to_tensor(item_vec,dtype = float32,name="items")
    print ('shape of H'+str(H.shape))
    
    
    regularizer = tf.multiply(tf.add(tf.reduce_sum(tf.square(coefmatrix)),tf.reduce_sum(tf.square(T_DIFF))),lda, name="regularize")
    
    return W,AC,  H,time_emb, T_DIFF, coefmatrix,regularizer
    


    
# Uses k-fold cross-validation to learn the best regularization
# parameter to use for either user or item bias.
def learn_bias_lda(ratings, num_folds, ldas, num_users, num_items, global_mean, max_iter, user_bias = True):
    labels = ratings[:,2]
    skf = StratifiedKFold(labels, num_folds)
    min_lda = None
    min_rmse = 0
    for lda in ldas:
        sum_rmses = 0
        W, H, reg = create_factors_for_bias(num_users, num_items, lda, user_bias)
        for train, test in skf:
            tr, finalw, finalh = mf(ratings[train,:], W, H, reg, global_mean, max_iter, 0.8)
            sum_rmses += tr
            print("Training rmse: %s, lda: %s" % (tr, lda))
        avg_rmse = sum_rmses / num_folds
        if min_lda == None:
            # This is our first lambda.
            min_lda = lda
            min_rmse = avg_rmse
        elif avg_rmse < min_rmse:
            # We did better than the last lambda.
            min_rmse = avg_rmse
            min_lda = lda
        else:
            # It's not going to get any better with the next lambda.
            break
    return min_lda

# Runs the factorizer for the given number of iterations and with the given
# regularization parameter to learn user bias from the training set.
def get_user_bias(ratings_tr, lda, num_users, num_items, global_mean, max_iter):
    W, H, reg = create_factors_for_bias(num_users, num_items, lda, True)
    tr,  finalw, finalh = mf(ratings_tr, W, H, reg, global_mean, max_iter, 0.8)
    return finalw

# Runs the factorizer for the given number of iterations and with the given
# regularization parameter to learn item bias from the training set.
def get_item_bias(ratings_tr, lda, num_users, num_items, global_mean, max_iter):
    W, H, reg = create_factors_for_bias(num_users, num_items, lda, False)
    tr, finalw, finalh = mf(ratings_tr, W, H, reg, global_mean, max_iter, 0.8)
    return finalh

    