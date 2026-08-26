import os
import trimesh
import numpy as np

input_folder = "items"
output_folder = "models_out"
os.makedirs(output_folder, exist_ok=True)

for folder in os.listdir(input_folder):
    for file in os.listdir(os.path.join(input_folder, folder)):
        if not file.endswith(".obj"):
            continue
        
        path = os.path.join(input_folder, folder, file)
        try:
            mesh = trimesh.load(path, force='mesh')
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            continue
        
        # Center the mesh
        mesh.vertices -= mesh.centroid

        # Align using PCA (optional)
        inertia = mesh.moment_inertia
        eigvals, eigvecs = np.linalg.eigh(inertia)
        R = eigvecs  # rotation matrix from PCA
        # Convert to 4x4 homogeneous matrix
        T = np.eye(4)
        T[:3, :3] = R.T  # inverse rotation to align axes
        mesh.apply_transform(T)

        # Scale to fit unit cube
        scale = 1.0 / mesh.scale
        mesh.apply_scale(scale)
        
        # Export normalized OBJ
        # out_path = os.path.join(output_folder, file)
        if folder:
            os.makedirs(os.path.join(output_folder, folder), exist_ok=True)
        out_path = os.path.join(output_folder, f"{folder}/{file}")
        mesh.export(out_path)
        print(f"Processed {file} -> {out_path}")
