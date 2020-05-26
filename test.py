import pickle

test_model = pickle.load(open('model2.pkl','rb'))
preds = test_model.predict([[34,5,5037,250.24]])

print(preds[0])