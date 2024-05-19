import mysql.connector #ini namanya modul. buat sambungkan program dengan database mysql
from prettytable import PrettyTable #ini modul untuk buat tabel cantik :3
from datetime import datetime, time #ini modul untuk tanggal dan waktu menyesuaikan dengan yang ada dilaptop

# def cek_waktu_operasional():
#     sekarang = datetime.now().time() # Menggunakan datetime.now() secara langsung
#     jam_buka = time(8, 0) # Menggunakan time dari datetime
#     jam_tutup = time(, 0) # Menggunakan time dari datetime

#     return jam_buka <= sekarang <= jam_tutup

def buat_koneksi(): #ini fungsi yang dikasi nama buat_koneksi. fungsinya yah buat koneksi antara program dan mysql. tanpa ini gak bisa tersambung
    return mysql.connector.connect( # buat memanggil fungsi conector() dari mysql.connector
        host="localhost", #semua ini parameter yang disesuaikan untuk disambungkan ke database. anggaplah kita catat alamatnya.
        user="root",
        password="",
        database="toko_sampurna", #ini disesuaikan sama nama database di phpmyadmin. harus sama namanya!
        autocommit=True #ini biar commit otomatis gitu. biar setiap program gak perlu tulis commit terus! contoh mydb.commit()
    )

class User: 
    def __init__(self, nama, password,): 
        self.nama = nama
        self.password = password



#==========BLUEPRINT ADMIN DAN PROSES MENUNYA==============
class admin(User): 
    def __init__(self, id_admin, nama, password): 
        super().__init__(nama, password) 
        self.id_admin= id_admin
        self.nama = nama
        self.password = password

    def lihat_produk(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Produk")
            produk = cursor.fetchall()

            if produk:
                table = PrettyTable(["ID Produk", "Nama", "Harga", "Stok"])
                for row in produk:
                    table.add_row([row[0], row[1], f"Rp{row[2]}.00", row[3]])
                print("\nDaftar Produk:")
                print(table)
            else:
                print("Belum ada produk yang tersedia!")
        except mysql.connector.Error as err:
            print("Gagal mengambil data produk:", err)
        finally:
            cursor.close()
            conn.close()
    
    def update_pemasukkan(self, total_pengeluaran):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            # Dapatkan pemasukkan sekarang
            cursor.execute("SELECT pemasukkan_sekarang FROM Pemasukkan ORDER BY id_pemasukkan DESC LIMIT 1")
            pemasukkan_sekarang = cursor.fetchone()[0]

            # Hitung pemasukkan terbaru setelah dikurangi total pengeluaran
            pemasukkan_terbaru = pemasukkan_sekarang - total_pengeluaran

            # Update pemasukkan terbaru ke tabel Pemasukkan
            cursor.execute("UPDATE pemasukkan SET pemasukkan_sekarang = %s, tanggal_update = %s ORDER BY id_pemasukkan DESC LIMIT 1",
                        (pemasukkan_terbaru, datetime.now()))

            conn.commit()
        except mysql.connector.Error as err:
            print("Gagal memperbarui pemasukkan:", err)
        finally:
            cursor.close()
            conn.close()


    def tambah_produk(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            self.lihat_produk()
            nama_produk = input("Masukkan nama produk: ")
            harga_produk = int(input("Masukkan harga produk: "))
            stok_produk = int(input("Masukkan stok produk: "))

            harga_modal = harga_produk - 2000  # Hitung harga modal per produk

            # Insert produk baru
            cursor.execute("INSERT INTO produk (nama_produk, harga_produk, stok_produk) VALUES (%s, %s, %s)",
                        (nama_produk, harga_produk, stok_produk))

            # Catat pengeluaran
            total_pengeluaran = harga_modal * stok_produk

            # Catat pengeluaran ke tabel Pengeluaran
            cursor.execute("INSERT INTO pengeluaran (id_produk, stok_baru, total_biaya, tanggal_pengeluaran) VALUES (%s, %s, %s, %s)",
                        (cursor.lastrowid, stok_produk, total_pengeluaran, datetime.now()))

            # Update tabel pemasukkan
            self.update_pemasukkan(total_pengeluaran)

            conn.commit()
            print("Produk berhasil ditambahkan!")
        except mysql.connector.Error as err:
            print("Gagal menambahkan produk:", err)
        finally:
            cursor.close()
            conn.close()

    def update_produk(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            self.lihat_produk()
            id_produk = int(input("Masukkan ID produk yang ingin diperbarui: "))
            nama_produk = input("Masukkan nama produk baru: ")
            harga_produk = int(input("Masukkan harga produk baru: "))
            tambahan_stok = int(input("Masukkan tambahan stok produk: "))

            # Dapatkan data produk sebelum diperbarui
            cursor.execute("SELECT stok_produk FROM Produk WHERE id_produk = %s", (id_produk,))
            stok_sebelumnya = cursor.fetchone()[0]

            # Update produk
            cursor.execute("UPDATE produk SET nama_produk = %s, harga_produk = %s, stok_produk = stok_produk + %s WHERE id_produk = %s",
                        (nama_produk, harga_produk, tambahan_stok, id_produk))

            # Catat pengeluaran
            total_pengeluaran = (harga_produk-2000) * tambahan_stok

            # Catat pengeluaran ke tabel Pengeluaran
            cursor.execute("INSERT INTO pengeluaran (id_produk, stok_baru, total_biaya, tanggal_pengeluaran) VALUES (%s, %s, %s, %s)",
                        (id_produk, tambahan_stok, total_pengeluaran, datetime.now()))

            # Update tabel pemasukkan
            self.update_pemasukkan(total_pengeluaran)

            conn.commit()
            print("Produk berhasil diperbarui!")
            
        except mysql.connector.Error as err:
            print("Gagal memperbarui produk:", err)
        finally:
            cursor.close()
            conn.close()

    def hapus_produk(self):
        self.lihat_produk()
        id_produk = int(input("Masukkan ID produk yang ingin dihapus: "))

        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            # Cek apakah ada ketergantungan referensial yang mengarah ke produk yang akan dihapus
            cursor.execute("SELECT COUNT(*) FROM penjualan_detail WHERE id_produk = %s", (id_produk,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print("Tidak dapat menghapus produk karena masih ada transaksi terkait.")
            else:
                # Jika tidak ada ketergantungan referensial, hapus produk dari tabel Produk
                query = "DELETE FROM Produk WHERE id_produk = %s"
                cursor.execute(query, (id_produk,))
                conn.commit()
                print("Produk berhasil dihapus!")
        except mysql.connector.Error as err:
            print("Gagal menghapus produk:", err)
        finally:
            cursor.close()
            conn.close()


    def total_pemasukkan(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            # Ambil total pemasukkan dari tabel Pemasukkan
            cursor.execute("SELECT SUM(pemasukkan_sekarang) FROM Pemasukkan")
            total_pemasukkan = cursor.fetchone()[0]
            if total_pemasukkan:
                print("Total pemasukkan: Rp", total_pemasukkan)
            else:
                print("Belum ada pemasukkan.")
        except mysql.connector.Error as err:
            print("Gagal mengambil total pemasukkan:", err)
        finally:
            cursor.close()
            conn.close()
    

    def total_pengeluaran(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_pengeluaran, id_produk, stok_baru, total_biaya, tanggal_pengeluaran FROM Pengeluaran")
            pengeluaran = cursor.fetchall()
            if pengeluaran:
                table = PrettyTable()
                table.field_names = ["ID Pengeluaran", "ID Produk", "Jumlah Stok Baru", "Total Biaya", "Tanggal Pengeluaran"]
                
                for data in pengeluaran:
                    id_pengeluaran, id_produk, stok_baru, total_biaya, tanggal_pengeluaran = data
                    table.add_row([id_pengeluaran, id_produk, stok_baru, f"Rp{total_biaya}", tanggal_pengeluaran])
                
                print("\nDaftar Pengeluaran:")
                print(table)
            else:
                print("Belum ada pengeluaran.")
        except mysql.connector.Error as err:
            print("Gagal mengambil pengeluaran:", err)
        finally:
            cursor.close()
            conn.close()



#==========BLUEPRINT PEMBELI DAN PROSES MENUNYA==============
class pembeli(User): 
    def __init__(self, id_pembeli, nama, password, no_hp, e_money): 
        super().__init__(nama, password) 
        self.id_pembeli = id_pembeli
        self.no_hp = no_hp
        self.e_money = e_money
    
    def lihat_produk(self):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Produk")
            produk = cursor.fetchall()

            if produk:
                table = PrettyTable(["ID Produk", "Nama", "Harga", "Stok"])
                for row in produk:
                    table.add_row([row[0], row[1], f"Rp{row[2]}.00", row[3]])
                print("\nDaftar Produk:")
                print(table)
            else:
                print("Belum ada produk yang tersedia!")
        except mysql.connector.Error as err:
            print("Gagal mengambil data produk:", err)
        finally:
            cursor.close()
            conn.close()
    
    def beli_produk(self):
        try:
            conn = buat_koneksi()
            cursor = conn.cursor()

            # Ambil jumlah e-money pengguna sebelum pembelian
            cursor.execute("SELECT e_money FROM pembeli WHERE id_pembeli = %s", (self.id_pembeli,))
            e_money_sebelum = cursor.fetchone()[0]

            # Tampilkan daftar produk
            self.lihat_produk()

            # Buat entri transaksi baru di tabel Penjualan
            total_harga = 0
            diskon = 0
            tanggal_penjualan = datetime.now()
            cursor.execute("INSERT INTO Penjualan (id_pembeli, total_harga, diskon, tanggal_penjualan) VALUES (%s, %s, %s, %s)", (self.id_pembeli, total_harga, diskon, tanggal_penjualan))
            id_penjualan = cursor.lastrowid

            while True:
                # Memasukkan ID Produk dan jumlah yang ingin dibeli
                id_produk = input("Masukkan ID Produk yang ingin dibeli (0 untuk keluar): ")
                if id_produk == '0':
                    break
                qty = int(input("Masukkan jumlah produk yang ingin dibeli: "))

                # Query untuk mengambil informasi produk yang akan dibeli
                cursor.execute("SELECT * FROM Produk WHERE id_produk = %s", (id_produk,))
                produk = cursor.fetchone()

                if not produk:
                    print("Produk tidak ditemukan.")
                    continue

                # Cek apakah stok mencukupi
                if produk[3] < qty:
                    print("Stok produk tidak mencukupi.")
                    continue

                subtotal = produk[2] * qty

                # Hitung total harga
                total_harga += subtotal

                # Masukkan detail pembelian ke dalam tabel Penjualan_Detail
                cursor.execute("INSERT INTO Penjualan_Detail (id_penjualan, id_produk, kuantitas, subtotal) VALUES (%s, %s, %s, %s)", (id_penjualan, id_produk, qty, subtotal))

                # Kurangi stok produk
                cursor.execute("UPDATE Produk SET stok_produk = stok_produk - %s WHERE id_produk = %s", (qty, id_produk))

            # Hitung diskon jika total pembelian lebih dari 100rb
            if total_harga >= 100000:
                diskon = 0.1 * total_harga

            # Hitung total harga setelah diskon
            total_harga_setelah_diskon = total_harga - diskon

            cursor.execute("UPDATE Penjualan SET total_harga = %s, diskon = %s WHERE id_penjualan = %s", (total_harga_setelah_diskon, diskon, id_penjualan))

            # Kurangi jumlah e-money pengguna
            sisa_e_money = e_money_sebelum - total_harga_setelah_diskon
            cursor.execute("UPDATE pembeli SET e_money = %s WHERE id_pembeli = %s", (sisa_e_money, self.id_pembeli))

            # Perbarui total pemasukkan dalam tabel Pemasukkan
            cursor.execute("UPDATE pemasukkan SET pemasukkan_sekarang = pemasukkan_sekarang + %s", (total_harga_setelah_diskon,))

            conn.commit()
            print("Pembelian berhasil.")

            cetak_invoice = input("\nApakah Anda ingin mencetak invoice? (y/n): ")
            if cetak_invoice.lower() == 'y':
                print("")
                self.menerima_invoice(id_penjualan, e_money_sebelum, sisa_e_money, total_harga, total_harga_setelah_diskon)

        except mysql.connector.Error as err:
            print("Gagal melakukan pembelian:", err)
        finally:
            cursor.close()
            conn.close()

    def menerima_invoice(self, id_penjualan, e_money_sebelum, e_money_sesudah, total_harga_sebelum_diskon, total_harga_setelah_diskon):
        try:
            conn = buat_koneksi()
            cursor = conn.cursor()

            # Ambil informasi pembelian dari tabel Penjualan dan Penjualan_Detail
            cursor.execute("SELECT p.tanggal_penjualan, pr.nama_produk, pd.kuantitas, pd.subtotal, p.diskon FROM Penjualan p JOIN Penjualan_Detail pd ON p.id_penjualan = pd.id_penjualan JOIN Produk pr ON pd.id_produk = pr.id_produk WHERE p.id_pembeli = %s AND p.id_penjualan = %s", (self.id_pembeli, id_penjualan))
            invoices = cursor.fetchall()

            if invoices:
                # Buat tabel untuk menampilkan invoice
                invoice_table = PrettyTable()
                invoice_table.field_names = ["Tanggal", "Nama Produk", "Jumlah", "Subtotal"]

                for invoice in invoices:
                    invoice_table.add_row([invoice[0], invoice[1], invoice[2], f"Rp{invoice[3]}"])

                # Cek apakah ada diskon
                diskon = invoices[0][4]

                # Tampilkan invoice menggunakan prettytable
                print("Invoice Transaksi Anda:")
                print(invoice_table)
                if diskon > 0:
                    print("DISKON:")
                    print(f"Diskon (10% untuk pembelian di atas Rp100.000): Rp{diskon:.2f}")
                elif diskon == 0:
                    print("DISKON:")
                    print(f"Diskon (10% untuk pembelian di atas Rp100.000): Rp{diskon:.2f}")
                print(f"Harga Sebelum Diskon: Rp{total_harga_sebelum_diskon:.2f}")
                print(f"Harga Setelah Diskon: Rp{total_harga_setelah_diskon:.2f}")
                print("\nTOTALAN:")
                print(f"Total Pembelian: Rp{total_harga_setelah_diskon:.2f}")
                print(f"e_Money Sebelum: Rp{e_money_sebelum:.2f}")
                print(f"e_Money Sesudah: Rp{e_money_sesudah:.2f}")
                print("                                    TERIMAKASIH -TOKO SAMPURNA")
            else:
                print("Belum ada transaksi pembelian.")

        except mysql.connector.Error as err:
            print("Gagal mengambil invoice:", err)
        finally:
            cursor.close()
            conn.close()

    def top_up_emoney(self, amount):
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            query = "UPDATE pembeli SET e_money = e_money + %s WHERE id_pembeli = %s"
            cursor.execute(query, (amount, self.id_pembeli))
            conn.commit()
            print("Top-up E-Money berhasil.")

            # Perbarui nilai e_money di objek pembeli setelah top-up
            self.e_money += amount
        except mysql.connector.Error as err:
            print("Gagal melakukan top-up E-Money:", err)
        finally:
            cursor.close()
            conn.close()


    def tampilkan_informasi_akun(self):   #ini fungsi untuk menampilkan fungsi pemilik akun yang sedang login
        # Tampilkan informasi akun masyarakat
        print("\n============INFORMASI AKUN===============") 
        print("Nama Lengkap:", self.nama)  
        print("Password:", self.password) 
        print("Nomor HP:", self.no_hp)  
        print("E-Money : Rp.", self.e_money)  

    def edit_informasi_akun(self):  #ini fungsi untuk mengedit informasi akun diatas. tapi cuma bisa edit nomor hape sama alamat. yang lain gak boleh!
        # Mengedit informasi akun masyarakat
        print("\nEdit Informasi Akun:")
        password_baru = input("Masukkan Password baru: ") #masukkan alamat baru dulu
        
        # Validasi nomor HP agar hanya berisi angka
        while True: #perulangan
            nomor_hp_baru = input("Masukkan nomor HP baru: ") #terus masukkan nomor hape baru
            if nomor_hp_baru.isdigit(): #nomor hape yang baru harus angka! kalau ngga gak boleh!
                break
            else:
                print("Nomor HP hanya boleh berisi angka. Silakan coba lagi.")

        # Lakukan validasi data yang dimasukkan sebelum melakukan pembaruan di database
        if password_baru.strip() == "" or nomor_hp_baru.strip() == "": #alamat baru dikasi strip() biar kalau ada spasi spasi gak jelas otomatis dihapus otomatis. nomor hape juga. kodisi mereka berdua gak boleh juga kosong
            print("Alamat dan nomor HP tidak boleh kosong. Silakan coba lagi.")
        else:
            # Lakukan pembaruan data di database
            conn = buat_koneksi() #Membuat koneksi baru ke database menggunakan fungsi buat_koneksi().
            cursor = conn.cursor() #Membuat objek cursor dari koneksi database yang diberikan.
            try:
                cursor.execute("UPDATE pembeli SET password = %s, no_hp = %s WHERE id_pembeli = %s",
                            (password_baru, nomor_hp_baru, self.id_pembeli)) #eksekusi query untuk mengupdate akun masyarakat dari table masyarakat
                conn.commit() #biasa dikasih pas ada query update data, tugasnya memastikan bahwa perubahan tersebut diterapkan secara permanen pada database.
                print("Informasi akun berhasil diperbarui.")
                self.password = password_baru  #nilai atribut diperbarui
                self.no_hp = nomor_hp_baru  
            except mysql.connector.Error as err: #ini kalau error querynya bisa dikasih tau errornya karena apa
                print("Gagal memperbarui informasi akun:", err)
            finally:
                cursor.close() #tutup cursor
                conn.close() #tutup koneksi

    def lihat_dan_edit_informasi_akun(self):  #nah ini buat nampilin fungsi menu edit akun diatas tadi
        while True: #perulangan while
            self.tampilkan_informasi_akun()  #memanggil fungsi tampilkan akun

            print("\n\033[0m\033[91m1.\033[0m Top up E-Money")
            print("\033[0m\033[91m2.\033[0m Edit Informasi Akun")
            print("\033[0m\033[91m3.\033[0m Kembali ke Menu Utama")

            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                amount = int(input("Masukkan jumlah top-up E-Money: "))
                self.top_up_emoney(amount)
            elif pilihan == "2":
                self.edit_informasi_akun() 
            elif pilihan == "3":
                # Kembali ke menu utama
                break #memberhentikan perulangan
            else:
                print("Pilihan tidak valid. Silakan pilih opsi yang valid.")


        

def menu_admin(admin): #ini fungsi menu_admin dan masih memiliki kaitan dengan class admin
    while True:
        # Tampilan menu admin
        print("\n\033[0m\033[91mMenu Admin:\033[0m")
        print("\033[0m\033[91m1.\033[0m Lihat Produk")
        print("\033[0m\033[91m2.\033[0m Kelola Produk")
        print("\033[0m\033[91m3.\033[0m Pendataan Keuangan")
        print("\033[0m\033[91m4.\033[0m Keluar")
        pilihan = input("Silahkan Pilih Menu(1/2/3/4): ")

        if pilihan == "1":
            admin.lihat_produk()
        elif pilihan == "2":
            while True:
                print("\n\033[0m\033[91mMenu CRUD Produk:\033[0m")
                print("\033[0m\033[91m1.\033[0m Tambah Produk")
                print("\033[0m\033[91m2.\033[0m Update Produk")
                print("\033[0m\033[91m3.\033[0m Hapus Produk")
                print("\033[0m\033[91m4.\033[0m Keluar")
                pilihan = input("Silahkan Pilih Menu(1/2/3/4): ")
                if pilihan == "1":
                    admin.tambah_produk()
                elif pilihan == "2":
                    admin.update_produk()
                elif pilihan == "3":
                    admin.hapus_produk()
                elif pilihan == "4":
                    break
                else:
                    print("Pilihan tidak valid. Silakan pilih menu yang benar.")
        elif pilihan == "3":
            while True:
                print("\n\033[0m\033[91mMenu Pendataan Produk:\033[0m")
                print("\033[0m\033[91m1.\033[0m Pemasukan Toko")
                print("\033[0m\033[91m2.\033[0m Pengeluaran Toko")
                print("\033[0m\033[91m3.\033[0m Keluar")
                pilihan = input("Silahkan Pilih Menu(1/2/3/4): ")
                if pilihan == "1":
                    admin.total_pemasukkan()
                elif pilihan == "2":
                    admin.total_pengeluaran()
                elif pilihan == "3":
                    break
        elif pilihan == "4":
            main()
            break
            
        else:
            print("Pilihan tidak valid. Silakan pilih menu yang benar.")

def menu_pembeli(pembeli):
    while True:
        print("\n\033[0m\033[91mMenu Pembeli:\033[0m")
        print("\033[0m\033[91m1.\033[0m Lihat Produk")
        print("\033[0m\033[91m2.\033[0m Beli Produk")
        print("\033[0m\033[91m3.\033[0m Informasi Akun")
        print("\033[0m\033[91m4.\033[0m Keluar")
        pilihan = input("Silahkan Pilih Menu(1/2/3/4): ")

        if pilihan == "1":
            pembeli.lihat_produk()
        elif pilihan == "2":
            pembeli.beli_produk()
        elif pilihan == "3":
            pembeli.lihat_dan_edit_informasi_akun()
        elif pilihan == "4":
            print("Keluar dari menu pembeli.")
            main()
            break
        else:
            print("Pilihan tidak valid. Silakan pilih menu yang benar.")

def buat_akun_pembeli(): 
    conn = buat_koneksi() 
    cursor = conn.cursor() 
    try:         
        nama = input("Masukkan nama lengkap Anda: ")
        password= input("Masukkan password Anda: ")
        
        no_hp = input("Masukkan nomor HP Anda: ")
        if not no_hp.isdigit(): 
            raise ValueError("Nomor HP harus berupa angka!")
        
        e_money = 0

        query = "INSERT INTO pembeli (nama, password, no_hp, e_money) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nama, password, no_hp, e_money)) #eksekusi query
        conn.commit()  #mengkonfirmasi bahwa perubahan yang dibuat bakal disimpan di database

        print("Akun pembeli berhasil dibuat.")
        main()
    except ValueError as ve: #Blok ini menangkap pengecualian yang dihasilkan jika terjadi kesalahan dalam pemrosesan nilai, ve dicetak dalam pesan yang mengindikasikan bahwa ada kesalahan dalam membuat akun masyarakat.
        print("Gagal membuat akun pembeli:", ve)
    except mysql.connector.Error as err: #ini kalau error querynya bisa dikasih tau errornya karena apa
        print("Gagal membuat akun pembeli:", err)
    finally:
        cursor.close() #tutup cursor
        conn.close() #tutup koneksi


def ambil_info_admin(username): 
    conn = buat_koneksi() 
    cursor = conn.cursor() 
    try: 
        cursor.execute("SELECT * FROM admin WHERE LOWER(nama) = LOWER(%s)", (username,)) 
        admin_data = cursor.fetchone() 
        if admin_data: 
            return admin(admin_data[0],admin_data[1], admin_data[2]) 
        else:
            return None
    except mysql.connector.Error as err: 
        print("Gagal mengambil info admin:", err)
    finally:
        cursor.close() #tutup cursor
        conn.close() #tutup koneksi

def ambil_info_pembeli(username):
    conn = buat_koneksi() 
    cursor = conn.cursor() 
    try: 
        cursor.execute("SELECT * FROM pembeli WHERE LOWER(nama) = LOWER(%s)", (username,)) 
        data_pembeli = cursor.fetchone()  # Ubah nama variabel tupel menjadi data_pembeli
        if data_pembeli:
            return pembeli(data_pembeli[0], data_pembeli[1], data_pembeli[2], data_pembeli[3], data_pembeli[4])  # Ubah nama variabel tupel menjadi data_pembeli
        else:
            return None
    except mysql.connector.Error as err: 
        print("Gagal mengambil info pembeli:", err)
    finally:
        cursor.close()
        conn.close()


def cek_login(username, password):
    conn = buat_koneksi()
    cursor = conn.cursor()
    try: 
        cursor.execute("SELECT * FROM admin WHERE nama = %s AND password = %s", (username, password)) 
        admin = cursor.fetchone() 
        if admin: 
            return "admin" 
        else:
            cursor.execute("SELECT * FROM pembeli WHERE nama = %s AND password = %s", (username, password)) 
            pembeli = cursor.fetchone()  

            if pembeli: 
                return "pembeli" 
            else:
                main()
    except mysql.connector.Error as err:  
        print("Gagal melakukan pengecekan login:", err)
    finally:
        cursor.close() #tutup cursor
        conn.close() #tutup koneksi

def main():
    # if not cek_waktu_operasional():
    #     print("Toko tutup. Silakan kembali pada jam operasional: 08:00 - 16:00")
    #     return
    
    print("")
    print("================WELOCOME================")
    print("     APLIKASI TOKO SAMPURNA JAHAYA      ")
    print("      PALING MURAH PALING LENGKAP       ")
    print("    JAM OPERASIONAL 08.00-16.00 WITA    ")
    print("========================================")    
    print("\nSilahkan pilih menu:")
    print("\033[0m\033[91m1.\033[0m Login")
    print("\033[0m\033[91m2.\033[0m Registrasi")

    while True:
        pilihan = input("Masukkan pilihan Anda (1/2): ")
        if pilihan.lower() == "1":
            print("")
            print("==================LOGIN=================")
            username = input("Masukkan Username Anda: ")
            password = input("Masukkan Password Anda: ")

            # Cek apakah pengguna terdaftar sebagai admin atau pembeli
            user_type = cek_login(username, password) 
            if user_type == "admin": 
                admin = ambil_info_admin(username) 
                if admin: 
                    print("Login berhasil sebagai admin!")
                    menu_admin(admin)
                    break
            elif user_type == "pembeli":
                pembeli = ambil_info_pembeli(username) 
                if pembeli: 
                    print("Login berhasil sebagai",(username),"!")
                    menu_pembeli(pembeli)  
                    break
            else:
                print("Nama pengguna atau kata sandi salah. Silakan coba lagi!")

        elif pilihan.lower() == "2":
            buat_akun_pembeli() #panggil fungsi untuk buat akun masyarakat

        else:
            print("Pilihan tidak ada!")

if __name__ == "__main__": #untuk mengeksekusi kode tertentu hanya jika skrip Python dieksekusi langsung, bukan diimpor sebagai modul oleh skrip lain.
    main() #tampilkan fungsi main() atau tampilan utama
