# -*- coding: utf-8 -*-

import pandas as pd #библиотека анализа данных с открытым исходным кодом
import numpy as np #библиотека для научных вычислений
import missingno as msno #библиотека которая помогает визуализировать недостающие данные в датафреймах Pandas
import seaborn as sns #библиотека визуализации данных Python, построенная поверх Matplotlib
import matplotlib.pyplot as plt #коллекция функций в стиле команд, которая позволяет использовать matplotlib почти так же, как MATLAB


#Игнорирование предупреждений
import warnings
warnings.filterwarnings("ignore")
# Чтение файлов обычно выглядит так:
df = pd.read_csv('gender_submission.csv')
test_data = pd.read_csv('test.csv')
print(test_data)
train_data = pd.read_csv('train.csv')
#Для изучения данных соединим train и test.
y = test_data.merge(df,on='PassengerId', how = 'right')
df = train_data.append(y)
#print(y)
#Классы билетов
df.groupby('Pclass')['PassengerId'].count()

#Мужчины-женщины на борту
df.groupby('Sex')['PassengerId'].count()

#Описательная статистика возраста пассажиров.
df.Age.describe()

#Визуализация шансов выжить в зависимости от пола и общее кол-во мужчин и женщин
fig, axarr = plt.subplots(1, 2, figsize=(12,6))
a = sns.countplot(train_data['Sex'], ax=axarr[0]).set_title('Кол-во мужчин и женщин')
axarr[1].set_title('Шансы выжить у разного пола')
b = sns.barplot(x='Sex', y='Survived', data=train_data, ax=axarr[1]).set_ylabel('Шансы выжить')

#Визуализация шансов выжить мужчин и женщин в зависимости от класса
plt.title('Шансы выжить у разного пола и классов')
g = sns.barplot(x='Pclass', y='Survived', hue='Sex', data=train_data).set_ylabel('Шансы выжить')

#Визуализация шансов выжить в зависимости от класса и общее кол-во выживших
fig, axarr = plt.subplots(1,2,figsize=(12,6))
a = sns.countplot(x='Pclass', hue='Survived', data=train_data, ax=axarr[0]).set_title('Выжившие и погибшие в классах')
axarr[1].set_title('Шансы выжить в разных классах')
b = sns.barplot(x='Pclass', y='Survived', data=train_data, ax=axarr[1]).set_ylabel('Survival rate')

predictors = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
mark="Survived"

def harmonize_data(titanic):
    #Пропущенные значения возраста заменяются медианным значением возраста
    titanic["Age"] = titanic["Age"].fillna(titanic["Age"].median())
    titanic["Age"].median()


    #Кодирование переменной "Sex" в числовой формат
    titanic.loc[titanic["Sex"] == "male", "Sex"] = 0
    titanic.loc[titanic["Sex"] == "female", "Sex"] = 1

    #Заполнение пропущенных значений переменной "Embarked" значением "S" и кодирование ее в числовой формат
    titanic["Embarked"] = titanic["Embarked"].fillna("S")

    titanic.loc[titanic["Embarked"] == "S", "Embarked"] = 0
    titanic.loc[titanic["Embarked"] == "C", "Embarked"] = 1
    titanic.loc[titanic["Embarked"] == "Q", "Embarked"] = 2
#Пропущенные значения переменной "Fare" заменяются медианным значением стоимости билета:
    titanic["Fare"] = titanic["Fare"].fillna(titanic["Fare"].median())

    return titanic

#кросс-валидация модели
from sklearn.model_selection import cross_val_score

def validation_scores(clf, train_data):
    scores = cross_val_score(
        clf,
        train_data[predictors],
        train_data[mark],
        cv=3
    )
    return scores.mean()

train_data = harmonize_data(train_data)
test_data  = harmonize_data(test_data)

# Функция, которая сравнивает производительность нескольких классификаторов на обучающих данных
def compare_metods(classifiers, train_data):
    names, scores = [], []
    for name, clf in classifiers:
        names.append(name)
        scores.append(validation_scores(clf, train_data))
    return pd.DataFrame(scores, index=names, columns=['Scores'])

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

classifiers = [
    ("Nearest Neighbors", KNeighborsClassifier(3)), #метод к-ближайших соседей
    ("Linear SVM", SVC(kernel="linear", C=0.025)), #классификации линейных опорных векторов
    ("RBF SVM", SVC(gamma=2, C=1)), #метод опорных векторов
    ("Gaussian Process",GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True)), #функция логистической связи
    ("Decision Tree", DecisionTreeClassifier(max_depth=5)), #дерево решений
    ("Random Forest", RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)), #случайный лес
    ("Neural Net", MLPClassifier(alpha=1)), #алгоритм многослойного перцептрона
    ("AdaBoost",AdaBoostClassifier()), #классификатор адабуст
    ("Naive Bayes", GaussianNB()), #наивный байесовский классификатор
    ("QDA", QuadraticDiscriminantAnalysis()) #линейный дискриминантный анализ
]

res = compare_metods(classifiers, train_data)
res

"""Строим график для сравнения классификаторов"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
res.plot(kind='bar', rot=90)
