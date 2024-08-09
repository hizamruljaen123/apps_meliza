$(document).ready(function() {
    $('#sidebarCollapse').on('click', function() {
      $('#sidebar').toggleClass('active');
    });
  
    $('#dataLatihLink').on('click', function() {
      // Panggil API untuk data latih dan tampilkan di tabel
      $.get('/get_data_latih', function(data) {
        populateTable(data);
      });
    });
  
    $('#dataUjiLink').on('click', function() {
      // Panggil API untuk data uji dan tampilkan di tabel
      $.get('/get_data_uji', function(data) {
        populateTable(data);
      });
    });
  
    function populateTable(data) {
      let tableBody = $('#tableBody');
      tableBody.empty();
      data.forEach((item, index) => {
        tableBody.append(`
          <tr>
            <td>${index + 1}</td>
            <td>${item.Nama_Keluarga}</td>
            <td>${item.Alamat}</td>
            <td>${item.Kabupaten}</td>
            <td>${item.Kecamatan}</td>
            <td>${item.Pendapatan_Per_Bulan}</td>
            <!-- Tambahkan kolom lain sesuai kebutuhan -->
          </tr>
        `);
      });
    }
  
    // Contoh untuk membuat grafik dengan Plotly.js
    function createPlotlyChart() {
      let data = [{
        x: [1, 2, 3, 4, 5],
        y: [10, 15, 13, 17, 21],
        type: 'scatter'
      }];
  
      Plotly.newPlot('plotlyChart', data);
    }
  
    // Panggil fungsi ini saat memuat data atau berdasarkan kebutuhan
    createPlotlyChart();
  });
  


  function data_latih() {
    $.get('http://127.0.0.1:5000/data_latih', function(data) {
        let tableBody = $('#data_latih');
        tableBody.empty();

        $('#data_latih_count').text(data.length);

        let kategoriCounts = {};

        data.forEach((item, index) => {
            tableBody.append(`
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.Nama_Keluarga}</td>
                    <td>${item.Alamat}</td>
                    <td>${item.Kabupaten}</td>
                    <td>${item.Kecamatan}</td>
                    <td>${formatRupiah(item.Pendapatan_Per_Bulan)}</td>
                    <td>${item.Jenis_Pekerjaan}</td>
                    <td>${item.Riwayat_Penyakit_Kronis}</td>
                    <td>${item.Tingkat_Pendidikan}</td>
                    <td>${item.Status_Kepemilikan_Rumah}</td>
                    <td>${item.Kehilangan_Mata_Pencaharian}</td>
                    <td>${item.Anggota_Keluarga_Rentan}</td>
                    <td>${item.Tidak_Menerima_Bantuan_Sosial}</td>
                    <td>${item.Rumah_Tangga_Lansia_Tunggal}</td>
                    <td>${item.Perempuan_Kepala_Keluarga}</td>
                    <td>${item.Kategori}</td>
                </tr>
            `);

            if (kategoriCounts[item.Kategori]) {
                kategoriCounts[item.Kategori]++;
            } else {
                kategoriCounts[item.Kategori] = 1;
            }
        });

        plotKategoriChart(kategoriCounts);
    });
}


function tambahDataLatih() {
  let formData = $('#dataLatihForm').serialize(); // Mengambil data dari form

  $.ajax({
      url: 'http://127.0.0.1:5000/add_data_latih', // URL endpoint Flask
      type: 'POST',
      data: formData, // Data yang dikirimkan
      success: function(response) {
          alert('Data berhasil disimpan!');
          $('#inputModal').modal('hide'); // Menutup modal setelah berhasil
          // Anda dapat menambahkan fungsi untuk memperbarui tabel data latih di sini
      },
      error: function(response) {
          alert('Terjadi kesalahan, data gagal disimpan.');
      }
  });
}

function tambahDataLatih() {
  let formData = $('#dataUjiForm').serialize(); // Mengambil data dari form

  $.ajax({
      url: 'http://127.0.0.1:5000/add_data_uji', // URL endpoint Flask
      type: 'POST',
      data: formData, // Data yang dikirimkan
      success: function(response) {
          alert('Data berhasil disimpan!');
          $('#inputModal').modal('hide'); // Menutup modal setelah berhasil
          // Anda dapat menambahkan fungsi untuk memperbarui tabel data latih di sini
      },
      error: function(response) {
          alert('Terjadi kesalahan, data gagal disimpan.');
      }
  });
}


function plotKategoriChart(kategoriCounts) {
    let kategori = Object.keys(kategoriCounts);
    let counts = Object.values(kategoriCounts);

    let data = [{
        x: kategori,
        y: counts,
        type: 'bar'
    }];

    let layout = {
        title: 'Kategori Data Latih',
        xaxis: {
            title: 'Kategori'
        },
        yaxis: {
            title: 'Jumlah'
        }
    };

    Plotly.newPlot('dataLatihChart', data, layout);
}

function data_uji() {
  $.get('http://127.0.0.1:5000/data_uji', function(data) {
      let tableBody = $('#data_uji');
      tableBody.empty();

      // Tampilkan jumlah data latih
      $('#data_uji_count').text(data.length);

      data.forEach((item, index) => {
          tableBody.append(`
              <tr>
                  <td>${index + 1}</td>
                  <td>${item.Nama_Keluarga}</td>
                  <td>${item.Alamat}</td>
                  <td>${item.Kabupaten}</td>
                  <td>${item.Kecamatan}</td>
                  <td>${formatRupiah(item.Pendapatan_Per_Bulan)}</td>
                  <td>${item.Jenis_Pekerjaan}</td>
                  <td>${item.Riwayat_Penyakit_Kronis}</td>
                  <td>${item.Tingkat_Pendidikan}</td>
                  <td>${item.Status_Kepemilikan_Rumah}</td>
                  <td>${item.Kehilangan_Mata_Pencaharian}</td>
                  <td>${item.Anggota_Keluarga_Rentan}</td>
                  <td>${item.Tidak_Menerima_Bantuan_Sosial}</td>
                  <td>${item.Rumah_Tangga_Lansia_Tunggal}</td>
                  <td>${item.Perempuan_Kepala_Keluarga}</td>
              </tr>
          `);
      });
  });
}
function formatRupiah(angka) {
  return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
  }).format(angka);
}

function loadAndPlotTestData() {
  $.get('http://127.0.0.1:5000/test', function(data) {
      let kategoriCounts = {};
      let tableBody = $('#hasil_klasifikasi');
      tableBody.empty(); // Kosongkan isi tabel sebelum menambahkan data baru

      data.forEach((item, index) => {
          // Hitung jumlah per kategori
          if (kategoriCounts[item['Kategori Prediksi']]) {
              kategoriCounts[item['Kategori Prediksi']]++;
          } else {
              kategoriCounts[item['Kategori Prediksi']] = 1;
          }

          // Tambahkan data ke tabel
          tableBody.append(`
              <tr>
                  <td>${index + 1}</td>
                  <td>${item['Nama_Keluarga']}</td>
                  <td>${item['Kategori Prediksi']}</td>
              </tr>
          `);
      });

      let kategori = Object.keys(kategoriCounts);
      let counts = Object.values(kategoriCounts);

      let plotData = [{
          x: kategori,
          y: counts,
          type: 'bar'
      }];

      let layout = {
          title: 'Hasil Klasifikasi',
          xaxis: {
              title: 'Kategori Prediksi'
          },
          yaxis: {
              title: 'Jumlah'
          }
      };

      Plotly.newPlot('hasilKlasifikasi', plotData, layout);
  });
}

data_latih()
data_uji()
loadAndPlotTestData()