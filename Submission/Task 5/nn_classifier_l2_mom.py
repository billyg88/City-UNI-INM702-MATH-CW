import pickle
import random # for shuffling the dataset at the start of an epoch 
import numpy as np
import matplotlib.pyplot as plt


"""
This is an implementation of a NN class, with RELU/Linear activation functions, and L2 regularization of weigths. 
 The weight update is a bit different from 
the simple NN.

"""


with open("Datasets/processed/training_data.pickle", "br") as fh:
    training_imgs = pickle.load(fh)
training_imgs_np = np.array(training_imgs)    
    
with open("Datasets/processed/training_labels.pickle", "br") as fh:
    training_labels = pickle.load(fh)
    
with open("Datasets/processed/training_labels_one_hot.pickle", "br") as fh:
    training_labels_one_hot = pickle.load(fh)
training_labels_one_hot_np = np.array(training_labels_one_hot)
    
with open("Datasets/processed/test_data.pickle", "br") as fh:
    testing_data = pickle.load(fh)    
test_imgs_np = np.array(testing_data)
    
with open("Datasets/processed/test_labels.pickle", "br") as fh:
    testing_labels = pickle.load(fh)      
    
test_labels = [int(label) for label in testing_labels]
    
    

#set seed for reproducible results

np.random.seed(8)
np.random.RandomState(8)



class billy_nn:
    
      
      
      
    def linear_activation_batch(self,matrix):
          
          return matrix

      
    def relu_activation_batch(self,matrix):
          
          
          return np.maximum(0,matrix)
    
      
    def relu_derivative_batch(self, matrix):
          
        matrix[matrix<=0] = 0
        matrix[matrix>0] = 1
        
        return matrix
  
      

      
    def softmax_activation_batch(self, matrix):
          
        z = matrix - np.max(matrix, axis=-1, keepdims=True) #prevent overflow here, with this 
        numerator = np.exp(z)
        denominator = np.sum(numerator,1)
        denominator = denominator.reshape(matrix.shape[0],-1) # (number of samples, 1)
        
        probs = numerator/denominator
        
        return probs      
          



    
    
    def __init__(self, architecture = [1024, 100, 10] , bias = False, activation = 'RELU',  learning_rate = 0.0015, 
                 regularizer_l2 = False, L2_term = 0.005, dropout = False, dropout_rate = 0.8, momentum_rate = 0.4):    
    
        self.bias = bias
        
        self.activation = activation
        
        self.architecture = architecture
        
        self.learning_rate = learning_rate
        
        self.regularizer_l2 = regularizer_l2
        
        self.L2_term = L2_term
        
        self.dropout = dropout
        
        self.dropout_rate = dropout_rate
        
        self.momentum_terms = []
        
        self.momentum_rate = momentum_rate # momentum rate muct be between (0,1)
        
        
        self.initialize_weights() #initialize weights by taking into account the architecture
        
      
        
    def initialize_weights(self):
            
            self.weights = []
            self.biases = []
                        
            for _ in range(len(self.architecture)-1):
                
                weight_matrix = np.random.normal(loc=0.0,scale=2/np.sqrt(self.architecture[_]+self.architecture[_+1]),
                                                 size=(self.architecture[_],self.architecture[_+1]))
                
                self.weights.append(weight_matrix)
                


                #
                ## COST FUNCTION UNDER REVIEW 
                #
  
    def calculate_cost_batch(self, probs, labels):
          
          losses = labels * np.log(probs+ 1e-5) # works against underflow
                    
          batch_loss = - losses.sum()
          
          return batch_loss


        
        
    def train_on_batch(self, batch_samples, batch_labels):
        
        
          if self.dropout == False:
                
                batch_probs, hidden_activations = self.forward_batch_propagation(batch_samples)
          
          else:
                
                batch_probs, hidden_activations, activation_mask = self.forward_batch_propagation_drop(batch_samples)
                      
          #calculate batch loss      
          batch_loss = self.calculate_cost_batch( batch_probs, batch_labels )
          self.batch_loss = batch_loss       
                
          ####update weights for the batch, first backpropagate the error, and then update each weight matrix
          if self.dropout == False : 
                
                self.update_weights_batch( batch_probs, hidden_activations, batch_labels, batch_samples )
                
          
          else:
                self.update_weights_batch_drop( batch_probs, batch_labels, batch_samples ,activation_mask) 
                
                
          return True       
                
                
                
                
                

          
    def forward_batch_propagation(self, batch_samples):
        
        # propagate the batch signal through the network, not using biases 
        input_batch = batch_samples
        hidden_activations = [] # needed for gradient calculation
        
        for weight in self.weights:
            
            trans_batch = np.dot(input_batch, weight) #matrix multiplication, no biasses added
            
            if weight.shape[1] == 4: #if we are multipying the by the final weight matrix
                #apply softmax activation to the batch
                probabilities_batch = self.softmax_activation_batch(trans_batch)
                break
                
                
            elif self.activation == 'RELU':   
                
                output_batch = self.relu_activation_batch(trans_batch)
                hidden_activations.append(output_batch)

            input_batch = output_batch
                
            
        return probabilities_batch, hidden_activations
                  
        

     
    def update_weights_batch(self, batch_probs, hidden_activations, batch_labels, batch_samples) :
          
          hidden_activations.reverse()
          
          output_layer_error = batch_probs - batch_labels # error to propagate 
          
          weights_list = list(self.weights)
          weights_list.reverse()
          
          
          layer_errors = []  # reverse this if needed
          
          layer_errors.append(output_layer_error.T)
         
          
          error_l = output_layer_error
          
          for i in range(len(weights_list)-1):
                
                error_term = np.dot(weights_list[i],error_l.T)
                
                if self.activation == 'RELU':
                
                      derivative_term = self.relu_derivative_batch(hidden_activations[i].T)
                                            
                
                error_l_minus = error_term * derivative_term
                
                layer_errors.append(error_l_minus)
                
                error_l = error_l_minus.T
                
                
          activations = list(hidden_activations)
          activations.reverse()
          
          activations.insert(0,batch_samples)
          activations.reverse()
          
          """
          for i in range(len(layer_errors)):
                                
                weight_update = np.dot(layer_errors[i],activations[i])
                
                 
                weight_update = weight_update +  (self.L2_term * weights_list[i].T)
                
                
                weights_list[i] -= self.learning_rate * weight_update.T #take some of the gradient using learning rate
                
          
          
          weights_list.reverse()
          
          self.weights = weights_list
          
          """
          
          
          
          
          if not self.momentum_terms: #if momentum terms have not been set... use regular GD and save the weight updates for next time
          
                for i in range(len(layer_errors)):
                                            
                      weight_gradient = np.dot(layer_errors[i],activations[i]) 
                      
                      weight_gradient = weight_gradient +  (self.L2_term * weights_list[i].T) #regularization term
                      
                      self.momentum_terms.append(weight_gradient)
                      
                      weights_list[i] -= self.learning_rate * weight_gradient.T 
                                      
                weights_list.reverse()
          

          else: # if the momentum terms DO exist, then use them for accelerating Gradient Descent!!!!!!!!
                
                momentum_terms = list(self.momentum_terms) 
               
                for i in range(len(layer_errors)):
                                            
                      weight_gradient = np.dot(layer_errors[i],activations[i])
                      
                                            
                      weight_gradient = weight_gradient +  (self.L2_term * weights_list[i].T) #regularization term

                      weight_update = (self.momentum_rate * momentum_terms[i]) + self.learning_rate * weight_gradient #momentum
                      
                      weights_list[i] -= weight_update.T 
                      
                      momentum_terms[i] = weight_update

                                      
                weights_list.reverse()      
                self.weights = weights_list
                self.momentum_terms = momentum_terms          
          

      
      
      
    def evaluate(self,data,labels):
        
        corrects, wrongs = 0, 0
        
        for i in range(len(data)):
              
            res = self.infer_sample(data[i])
            #sumaaaaaaaaaaaa = res.sum()
            res_max = res.argmax()
            #ruin=labels[i]
            
            if res_max == labels[i]:
                corrects += 1
            else:
                wrongs += 1
        return corrects, wrongs    




    def infer_sample(self,sample):
        #use this function to get a sample prediction, after the network has been trained   
        prediction = self.signal_propagation_test(sample)
          
        return prediction  
  
   
    def signal_propagation_test(self,sample):
                              
          trans_vector = sample
          
          for weight in self.weights:
                
                trans_vector = np.dot(trans_vector, weight) # matrix transformation 
                
                trans_vector = self.relu_activation_batch(trans_vector) # relu activation, no bias added
                
          prediction = trans_vector 
          
          return prediction
                
            
            
            
### Modelling
        
nn = billy_nn( architecture = [2304,100,100,4], bias = False, activation = 'RELU',  learning_rate = 0.0001,
              regularizer_l2 = True, L2_term = 0.05,  momentum_rate = 0.4)     

print('\n')
weights = nn.weights





# Mini-batch gradient descent 
batch_size = 1 #size of the mini-batch is 1 for Stochastic gradient descent
epochs = 500 
iteration_losses = [] #should be the same len aas the number of iteratios
epoch_accuracies = []
epoch_costs = [] # should match the number of epochs set


#Print training elements
num_of_batches = round(training_imgs_np.shape[0] / batch_size) + 1
num_of_iterations = epochs * num_of_batches

print ('\n Batch size',batch_size )
print('_________________________________________________')


print ('\n Number of batches per epoch',num_of_batches )
print('_________________________________________________')

print ('\n Number of iterations to perform:',num_of_iterations )
print('_________________________________________________')
print ('\n Momentum rate:', nn.momentum_rate )
print('_________________________________________________\n')



print ("Started regularized training with Momentum")

print('\n**************************************************')


#for each epoch 
for epoch in range(epochs):

            # cycle through all minibatches of data
            n_samples = training_imgs_np.shape[0]
            #shuffle entire dataset indices for proper mini-batch GD
            indices = np.arange(training_imgs_np.shape[0])
            np.random.shuffle(indices)
            
            for start in range(0, n_samples, batch_size):
            
                  end = min (start + batch_size, n_samples)
                  batch_indices = indices[start:end]
                  
                  #train nn on mini-batch data
                  nn.train_on_batch(training_imgs_np[batch_indices],training_labels_one_hot_np[batch_indices])
                  
                  #get mnin-batch crooss-entriopy loss term 
                  cel = nn.batch_loss
                  
                  #create l2 term for loss calculation
                  #l2_cost = (nn.L2_term / 2) * np.sum(np.square(nn.weights))
                  
                  weight_squared_sums = [np.sum(np.square(weight_matrix)) for weight_matrix in nn.weights]
                  
                  l2_cost = (nn.L2_term / 2) * np.array(weight_squared_sums).sum()
            
                  overall_cost = cel + l2_cost                       
                  
                  #save loss on the mini-batch
                  iteration_losses.append(overall_cost)
                  
            epoch_loss = iteration_losses[-num_of_batches:] 
            epoch_costs.append(np.array(epoch_loss).sum())

            
            #Evaluate training accuracy after each iteration
            corrects, wrongs = nn.evaluate(training_imgs_np, training_labels) #this is the integer representation
            accu = corrects / ( corrects + wrongs)
            print('_________________________________________________\n')
            print("Training accuracy after epoch ", accu, '\n')
            epoch_accuracies.append(accu)
            
            #epoch completed 
            print ("Epochs completed {} / {} ".format(epoch+1,epochs))

      



plt.plot(range(num_of_iterations), iteration_losses)
plt.ylabel('Cost')
plt.xlabel('Iterations')
#plt.savefig('loss.png', dpi=300)
plt.show()




plt.plot(range(epochs), epoch_accuracies)
plt.ylabel('Accuracy %')
plt.xlabel('Epochs')
#plt.savefig('loss.png', dpi=300)
plt.show()


plt.plot(range(epochs), epoch_costs)
plt.ylabel('Cost')
plt.xlabel('Epochs')
#plt.savefig('loss.png', dpi=300)
plt.show()




### Test the network with no training 
corrects, wrongs = nn.evaluate(test_imgs_np, test_labels)
print("\n  Testing accuracy after training ", corrects / ( corrects + wrongs), '\n')












