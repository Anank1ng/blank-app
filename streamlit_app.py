import streamlit as st
import time
import random

# Game setup
st.title("Flappy Bird Sederhana")

# Variabel game
bird_pos = 5  # Posisi burung
bird_velocity = 0  # Kecepatan vertikal burung
gravity = -1  # Gaya gravitasi
jump_strength = 3  # Kekuatan lompatan burung
pipe_pos = 10  # Posisi pipa pertama
pipe_gap = 3  # Jarak kosong antara pipa
pipe_width = 1  # Lebar pipa
score = 0  # Skor permainan
game_over = False  # Status permainan

# Fungsi untuk menampilkan area permainan
def display_game(bird_pos, pipe_pos, score, game_over):
    game_area = [' '] * 10
    # Menambahkan burung (B) dan pipa (|) ke area permainan
    if bird_pos < len(game_area):
        game_area[bird_pos] = 'B'  # B untuk burung
    for i in range(pipe_pos, pipe_pos + pipe_width):
        if i < len(game_area):
            game_area[i] = '|'
    game_str = ''.join(game_area)
    
    st.write(game_str)  # Menampilkan area permainan
    st.write(f"Skor: {score}")
    if game_over:
        st.write("Game Over!")
        
# Fungsi untuk menggerakkan pipa
def move_pipe(pipe_pos):
    return pipe_pos - 1 if pipe_pos > 0 else 10

# Fungsi untuk menggerakkan burung
def move_bird(bird_pos, bird_velocity):
    bird_pos += bird_velocity
    bird_velocity += gravity  # Menerapkan gravitasi
    # Membatasi burung agar tidak keluar dari batas
    if bird_pos < 0:
        bird_pos = 0
    if bird_pos >= 10:
        bird_pos = 9
    return bird_pos, bird_velocity

# Aksi lompat (up)
def jump(bird_velocity):
    return jump_strength

# Streamlit interactivity
if not game_over:
    # Input pengguna (klik untuk melompat)
    if st.button("Lompat (Klik untuk Lompat)"):
        bird_velocity = jump(bird_velocity)

    # Menggerakkan burung dan pipa
    bird_pos, bird_velocity = move_bird(bird_pos, bird_velocity)
    pipe_pos = move_pipe(pipe_pos)
    
    # Mengecek tabrakan burung dengan pipa
    if pipe_pos == 0 and bird_pos in range(0, pipe_gap):
        game_over = True
    elif pipe_pos == 0 and bird_pos not in range(0, pipe_gap):
        score += 1  # Menambah skor jika melewati pipa
    
    # Menampilkan game
    display_game(bird_pos, pipe_pos, score, game_over)
    
    # Memberikan waktu agar pengguna bisa melihat perubahan
    time.sleep(0.2)
