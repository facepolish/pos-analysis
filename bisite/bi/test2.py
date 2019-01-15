import matplotlib.pyplot as plt
import pandas as pd

if __name__=='__main__':

    plt.rcParams['font.family'] = 'IPAexGothic'
    test_df = pd.DataFrame(columns=['Xデータ', 'Yデータ','Zデータ'])

    test_df['Xデータ'] = [1,2,3,4]
    test_df['Yデータ'] = [1,2,3,4]
    test_df['Zデータ'] = ['あいうえお','愛上大','かきくけこ','牡蠣区家子']
    z_data = test_df.plot.scatter(x="Xデータ",y="Yデータ",figsize=(8, 6),s=30)

    # 各要素にラベルを表示
    for k, v in test_df.iterrows():
        z_data.annotate(v[2], xy=(v[0],v[1]), size=15)
    plt.show()
