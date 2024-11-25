import numpy as np
import matplotlib.pyplot as plt

def plot_result(results, news_site):
    x = np.array(range(0,len(results)))
    #positive
    y1 = np.vectorize(lambda result: result["positive_result"])(results)
    plt.title(f"plotting the sentiment of {news_site}")
    coef1 = np.polyfit(x,y1,10)
    pos_fn = np.poly1d(coef1) 
    #negative
    #The difference between the positive and the negative value
    y2 = np.vectorize(lambda result: result["negative_result"])(results)
    coef2 = np.polyfit(x,y2,10)
    neg_fn = np.poly1d(coef2) 
    plt.plot(x,y1,x,y2)
    plt.plot(pos_fn(x), color="#0e7800", linestyle="dashed") #positive is blue
    plt.plot(neg_fn(x), color="#ed1103", linestyle="dashed") #negative is red
    plt.show()


    #The difference between the positive and the negative value
    y = y1 - y2
    coef = np.polyfit(x,y,10)
    poly1d_fn = np.poly1d(coef) 
    plt.plot(x,y, 'yo', x, poly1d_fn(x), '--k')
    plt.show()


if __name__=="__main__":
    plot_result()