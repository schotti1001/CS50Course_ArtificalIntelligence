AI to identify which traffic sign appears in a photograph

To run:
pip3 install -r requirements.txt
#Example call:
python traffic.py gtsrb model.h5

Actions for finished model:

1. Started off with the example from the Tensorflow with several Conv2D and MaxPolling2D layers to get a general feeling
    -> Because of missing parameters in the compile function it didn´t work
2. Next attempt was the example from the video 
    -> loss: 0.64, accuracy 0.90
3. Tried again to adapt it to the Tensorflow example, but a few changes where necessary. Ended up with 2 new pooling layers and 2 new convolution layers
    -> loss: 0.1597 - accuracy: 0.9627
4. Removed a global max polling layer
    -> loss: 0.1243 - accuracy: 0.9717
5. Changed matrix size of pooling layer
    -> loss: 0.1917 - accuracy: 0.9527
6. Reduced dropout
    -> loss: 0.1638 - accuracy: 0.9636
7. Increased dropout
    -> loss: 0.9144 - accuracy: 0.7223
8. dropout  to 0.6
    ->loss: 0.2265 - accuracy: 0.9405
8. dopout back to 0.5
    -> loss: 0.1914 - accuracy: 0.9486
9. made one pooling matrix smaller and added an extra convolution layer
    -> oss: 0.1119 - accuracy: 0.9738
10. changed size of one convolution layer
    -> loss: 0.0848 - accuracy: 0.9813
11. changed size of one convolution layer again
    -> oss: 0.0834 - accuracy: 0.9835
12. changed size again
    -> loss: 0.0739 - accuracy: 0.9831
13. added a hidden layer
    -> loss: 0.1717 - accuracy: 0.9622
14. moved hidden layer
    -> loss: 0.1024 - accuracy: 0.9754
15. added hidden layer
    -> loss: 0.0821 - accuracy: 0.979
16. changed size of hidden and added some more
    -> loss: 0.1125 - accuracy: 0.9725
----> Conclusion seems like 0.98 is the possible best going to remove the hidden layers
Final Result: 
loss: 0.0865 - accuracy: 0.9798

