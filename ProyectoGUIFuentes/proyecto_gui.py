# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys

class MiniZincInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto de optimización discreta en MiniZinc (MinPol)")
        
        if not self.verificar_minizinc():
            messagebox.showerror("Error", 
                "MiniZinc no está instalado o no está en el PATH del sistema.\n\n"
                "Por favor:\n"
                "1. Descarga MiniZinc desde https://www.minizinc.org/\n"
                "2. Instálalo en tu sistema\n"
                "3. Asegúrate de que está en el PATH del sistema\n"
                "4. Vuelve a ejecutar esta aplicación")
            sys.exit(1)
            
        self.parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.mpl_path = tk.StringVar()
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.crear_widgets()
        
        self.resultado_text = tk.Text(self.main_frame, height=10, width=80)
        self.resultado_text.grid(row=3, column=0, columnspan=2, pady=10)

    def verificar_minizinc(self):
        """Verifica si MiniZinc está instalado y disponible en el sistema"""
        try:
            subprocess.run(["minizinc", "--version"], 
                        capture_output=True, 
                        text=True)
            return True
        except FileNotFoundError:
            return False
        
    def crear_widgets(self):
        file_frame = ttk.LabelFrame(self.main_frame, text="Configuración de archivos", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(file_frame, text="Archivo de datos (.mpl):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.mpl_path, width=80).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Buscar", command=self.buscar_mpl).grid(row=0, column=2, padx=5)
        
        # Botón para generar archivo y ejecutar modelo
        ttk.Button(self.main_frame, 
                text="Convertir y Ejecutar", 
                command=self.procesar_archivos).grid(row=2, column=0, 
                columnspan=2, pady=20)

    def buscar_mpl(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("MPL files", "*.mpl"), ("All files", "*.*")]
        )
        if filename:
            self.mpl_path.set(filename)

    def leer_archivo_mpl(self, filepath):
        """Lee y parsea el archivo MPL"""
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
                # Leer valores según la estructura definida
                n = int(lines[0].strip())
                m = int(lines[1].strip())
                pi = [int(x) for x in lines[2].strip().split(',')]
                vi = [float(x) for x in lines[3].strip().split(',')]
                cei = [float(x) for x in lines[4].strip().split(',')]
                
                # Leer matriz de costos
                ci = []
                for i in range(m):
                    row = [float(x) for x in lines[5+i].strip().split(',')]
                    ci.append(row)
                
                # Leer ct y maxM
                ct = float(lines[5+m].strip())
                maxM = int(lines[6+m].strip())
                
                return {
                    'n': n,
                    'm': m,
                    'pi': pi,
                    'vi': vi,
                    'cei': cei,
                    'ci': ci,
                    'ct': ct,
                    'maxM': maxM
                }
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo MPL: {str(e)}")
            return None

    def generar_dzn(self, datos):
        """Genera el archivo DZN en el mismo directorio que el script"""
        try:
            output_path = os.path.join(self.parent_dir, "DatosProyecto.dzn")
            with open(output_path, 'w') as f:
                f.write(f"n = {datos['n']};\n")
                f.write(f"m = {datos['m']};\n")
                f.write(f"pi = {datos['pi']};\n")
                f.write(f"vi = {datos['vi']};\n")
                f.write(f"cei = {datos['cei']};\n")
                
                f.write(f"ci = array2d(1..{datos['m']}, 1..{datos['m']}, [\n")
                for i, row in enumerate(datos['ci']):
                    f.write('    ' + ', '.join(str(x) for x in row))
                    if i < len(datos['ci']) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')
                f.write("]);\n")
                
                f.write(f"ct = {datos['ct']};\n")
                f.write(f"maxM = {datos['maxM']};\n")
                
            return output_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar archivo DZN: {str(e)}")
            return None

    def ejecutar_modelo(self, dzn_path):
        try:
            modelo_path = os.path.join(self.parent_dir, "Proyecto.mzn")
            if not os.path.exists(modelo_path):
                raise FileNotFoundError(f"No se encontró el archivo modelo.mzn en el directorio {self.parent_dir}")
            
            resultado = subprocess.run(
                ["minizinc", "--solver", "Gecode", "--time-limit", "30000", modelo_path, dzn_path],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            self.resultado_text.delete(1.0, tk.END)
            
            if resultado.returncode == 0:
                output = resultado.stdout
                
                lines = output.split('\n')
                formatted_output = ""
                for line in lines:
                    line = line.replace('"', '').strip()
                    if line:
                        formatted_output += line + "\n"
                
                self.resultado_text.insert(tk.END, formatted_output)
            else:
                self.resultado_text.insert(tk.END, f"Error: {resultado.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el modelo: {str(e)}")

    def procesar_archivos(self):
        """Procesa los archivos MPL y MZN"""
        if not self.mpl_path.get():
            messagebox.showerror("Error", "Por favor seleccione un archivo de datos (.mpl)")
            return
            
        # Leer datos del archivo MPL
        datos = self.leer_archivo_mpl(self.mpl_path.get())
        if datos:
            # Generar archivo DZN
            dzn_path = self.generar_dzn(datos)
            if dzn_path:
                # Ejecutar el modelo
                self.ejecutar_modelo(dzn_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniZincInterface(root)
    root.mainloop()