from flask import Flask, jsonify, render_template, request
import pandas as pd
import mysql.connector
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import joblib
import os
from sklearn.decomposition import PCA


app = Flask(__name__)

MODEL_PATH = 'svm_model.pkl'
SCALER_PATH = 'scaler.pkl'
GRAPH_PATH = 'static/graph/'

os.makedirs(GRAPH_PATH, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="data_svm"
    )

def load_and_prepare_training_data():
    conn = get_db_connection()
    query = "SELECT * FROM data_latih"
    df = pd.read_sql(query, conn)
    conn.close()

    label_encoders = {}
    categorical_columns = [
        'Jenis_Pekerjaan', 'Riwayat_Penyakit_Kronis', 'Tingkat_Pendidikan', 'Status_Kepemilikan_Rumah',
        'Kehilangan_Mata_Pencaharian', 'Anggota_Keluarga_Rentan', 'Tidak_Menerima_Bantuan_Sosial',
        'Rumah_Tangga_Lansia_Tunggal', 'Perempuan_Kepala_Keluarga'
    ]
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    X = df.drop(columns=['id', 'Nama_Keluarga', 'Alamat', 'Kabupaten', 'Kecamatan', 'Kategori'])
    y = df['Kategori'].apply(lambda x: 1 if x == 'Miskin Ekstrim' else 0)
    return X, y, df

def load_and_prepare_test_data():
    conn = get_db_connection()
    query = "SELECT * FROM data_uji"
    df = pd.read_sql(query, conn)
    conn.close()

    categorical_columns = [
        'Jenis_Pekerjaan', 'Riwayat_Penyakit_Kronis', 'Tingkat_Pendidikan', 'Status_Kepemilikan_Rumah',
        'Kehilangan_Mata_Pencaharian', 'Anggota_Keluarga_Rentan', 'Tidak_Menerima_Bantuan_Sosial',
        'Rumah_Tangga_Lansia_Tunggal', 'Perempuan_Kepala_Keluarga'
    ]
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
    X_test = df.drop(columns=['id', 'Nama_Keluarga', 'Alamat', 'Kabupaten', 'Kecamatan'])
    return X_test, df

def train_model(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = SVC(kernel='linear', random_state=42)
    model.fit(X_train_scaled, y_train)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    return model, scaler

def test_model(model, scaler, X_test):
    X_test_scaled = scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)
    return predictions

def evaluate_model(y_test, predictions):
    accuracy = accuracy_score(y_test, predictions)
    cm = confusion_matrix(y_test, predictions)
    return accuracy, cm

def visualize_results(cm, accuracy, predictions, X_test, y_test, df, model, scaler, file_name):
    # Confusion Matrix
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Prediksi')
    plt.ylabel('Aktual')
    plt.title(f'Akurasi: {accuracy * 100:.2f}%')
    plt.savefig(os.path.join(GRAPH_PATH, f'{file_name}_cm.png'))
    plt.close()

    # Reduksi dimensi menggunakan PCA
    pca = PCA(n_components=2)
    X_test_scaled = scaler.transform(X_test)
    X_test_pca = pca.fit_transform(X_test_scaled)

    # SVM Decision Boundary Visualization
    plt.figure(figsize=(15, 10))
    
    # Create a mesh to plot in
    x_min, x_max = X_test_pca[:, 0].min() - 1, X_test_pca[:, 0].max() + 1
    y_min, y_max = X_test_pca[:, 1].min() - 1, X_test_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))
    
    # Fit a new SVM model on PCA-transformed data
    from sklearn.svm import SVC
    svm_pca = SVC(kernel='linear', random_state=42)
    svm_pca.fit(X_test_pca, y_test)
    
    # Get the separating hyperplane
    Z = svm_pca.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    # Plot the decision boundary and margins
    plt.contourf(xx, yy, Z, levels=[-1, 0, 1], alpha=0.5,
                 colors=['#FFAAAA', '#AAAAFF'])
    plt.contour(xx, yy, Z, colors=['red', 'black', 'blue'], linestyles=['--', '-', '--'], levels=[-1, 0, 1])
    
    # Plot the training points
    scatter = plt.scatter(X_test_pca[:, 0], X_test_pca[:, 1], c=y_test, cmap=plt.cm.RdYlBu, edgecolor='black')
    
    # Plot the support vectors
    plt.scatter(X_test_pca[svm_pca.support_, 0], X_test_pca[svm_pca.support_, 1], s=100,
                linewidth=1, facecolors='none', edgecolors='k')
    
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title('SVM Decision Boundary with Support Vectors (PCA)')
    plt.colorbar(scatter)
    
    # Add legend
    handles, labels = scatter.legend_elements()
    plt.legend(handles, ['Miskin', 'Miskin Ekstrim'], loc="upper right", title="Kategori")
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPH_PATH, f'{file_name}_svm_decision_boundary.png'))
    plt.close()

    # Feature importance visualization
    if hasattr(model, 'coef_'):
        feature_importance = abs(model.coef_[0])
        feature_names = X_test.columns
        sorted_idx = np.argsort(feature_importance)
        pos = np.arange(sorted_idx.shape[0]) + .5

        plt.figure(figsize=(12, 8))
        plt.barh(pos, feature_importance[sorted_idx], align='center')
        plt.yticks(pos, np.array(feature_names)[sorted_idx])
        plt.xlabel('Feature Importance')
        plt.title('Feature Importance (SVM Coefficients)')
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPH_PATH, f'{file_name}_feature_importance.png'))
        plt.close()



# The train function remains the same
@app.route('/train', methods=['GET'])
def train():
    X, y, df = load_and_prepare_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model, scaler = train_model(X_train, y_train)
    predictions = test_model(model, scaler, X_test)
    accuracy, cm = evaluate_model(y_test, predictions)
    visualize_results(cm, accuracy, predictions, X_test, y_test, df, model, scaler, 'training')
    return jsonify({
        'message': 'Model berhasil dilatih dan disimpan',
        'accuracy': accuracy,
        'confusion_matrix': cm.tolist(),
        'graphs': {
            'confusion_matrix': f'static/graph/training_cm.png',
            'svm_decision_boundary': f'static/graph/training_svm_decision_boundary.png',
            'feature_importance': f'static/graph/training_feature_importance.png'
        }
    })

@app.route('/test', methods=['GET'])
def test():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return jsonify({'error': 'Model belum dilatih. Silakan latih model terlebih dahulu.'}), 400
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    X_test_new, test_df = load_and_prepare_test_data()
    predictions = test_model(model, scaler, X_test_new)
    test_df['Kategori Prediksi'] = ['Miskin Ekstrim' if pred == 1 else 'Miskin' for pred in predictions]
    return jsonify(test_df[['Nama_Keluarga', 'Kategori Prediksi']].to_dict(orient='records'))

@app.route('/data_latih', methods=['GET'])
def get_data_latih():
    conn = get_db_connection()
    query = "SELECT * FROM data_latih"
    df = pd.read_sql(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route('/data_uji', methods=['GET'])
def get_data_uji():
    conn = get_db_connection()
    query = "SELECT * FROM data_uji"
    df = pd.read_sql(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route('/add_data_latih', methods=['POST'])
def add_data_latih():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query SQL untuk menambahkan data ke dalam tabel
    sql = """INSERT INTO data_latih 
             (Nama_Keluarga, Alamat, Kabupaten, Kecamatan, Pendapatan_Per_Bulan,
              Jenis_Pekerjaan, Riwayat_Penyakit_Kronis, Tingkat_Pendidikan, 
              Status_Kepemilikan_Rumah, Kehilangan_Mata_Pencaharian, 
              Anggota_Keluarga_Rentan, Tidak_Menerima_Bantuan_Sosial, 
              Rumah_Tangga_Lansia_Tunggal, Perempuan_Kepala_Keluarga, Kategori) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Mengambil data dari form dan memasukkannya ke dalam query
    values = (
        data['Nama_Keluarga'],
        data['Alamat'],
        data['Kabupaten'],
        data['Kecamatan'],
        data['Pendapatan_Per_Bulan'],
        data['Jenis_Pekerjaan'],
        data['Riwayat_Penyakit_Kronis'],
        data['Tingkat_Pendidikan'],
        data['Status_Kepemilikan_Rumah'],
        data['Kehilangan_Mata_Pencaharian'],
        data['Anggota_Keluarga_Rentan'],
        data['Tidak_Menerima_Bantuan_Sosial'],
        data['Rumah_Tangga_Lansia_Tunggal'],
        data['Perempuan_Kepala_Keluarga'],
        data['Kategori']
    )

    try:
        # Menjalankan query dan commit perubahan
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({'message': 'Data berhasil disimpan!'}), 200
    except Exception as e:
        # Jika ada kesalahan, kembalikan pesan error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/add_data_uji', methods=['POST'])
def add_data_uji():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query SQL untuk menambahkan data ke dalam tabel
    sql = """INSERT INTO data_uji 
             (Nama_Keluarga, Alamat, Kabupaten, Kecamatan, Pendapatan_Per_Bulan,
              Jenis_Pekerjaan, Riwayat_Penyakit_Kronis, Tingkat_Pendidikan, 
              Status_Kepemilikan_Rumah, Kehilangan_Mata_Pencaharian, 
              Anggota_Keluarga_Rentan, Tidak_Menerima_Bantuan_Sosial, 
              Rumah_Tangga_Lansia_Tunggal, Perempuan_Kepala_Keluarga) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Mengambil data dari form dan memasukkannya ke dalam query
    values = (
        data['Nama_Keluarga'],
        data['Alamat'],
        data['Kabupaten'],
        data['Kecamatan'],
        data['Pendapatan_Per_Bulan'],
        data['Jenis_Pekerjaan'],
        data['Riwayat_Penyakit_Kronis'],
        data['Tingkat_Pendidikan'],
        data['Status_Kepemilikan_Rumah'],
        data['Kehilangan_Mata_Pencaharian'],
        data['Anggota_Keluarga_Rentan'],
        data['Tidak_Menerima_Bantuan_Sosial'],
        data['Rumah_Tangga_Lansia_Tunggal'],
        data['Perempuan_Kepala_Keluarga'],
    )

    try:
        # Menjalankan query dan commit perubahan
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({'message': 'Data berhasil disimpan!'}), 200
    except Exception as e:
        # Jika ada kesalahan, kembalikan pesan error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
