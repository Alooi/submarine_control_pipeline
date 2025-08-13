import torch
from PIL import Image
import cv2
import numpy as np

# --- Model and Device Setup ---
from depth_anything_processor import DepthAnythingProcessor
from frame_red_squares import RedSquaresGrid

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

class ObstacleDetector:
    def __init__(self, encoder='vits', red_squares_arc="ImageReducer_bounded_grayscale", red_squares_run_name="run_2", use_gpu=True):
        """
        Initializes the obstacle detection system.

        Args:
            encoder (str): The encoder to use for the Depth Anything model.
            red_squares_arc (str): The architecture for the RedSquaresGrid model.
            red_squares_run_name (str): The run name for the RedSquaresGrid model.
            use_gpu (bool): Whether to use GPU if available.
        """
        self.device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
        print(f"Using device: {self.device}")

        self.depth_processor = DepthAnythingProcessor(encoder=encoder, device=self.device)
        self.obstacle_grid_model = RedSquaresGrid(arc=red_squares_arc, run_name=red_squares_run_name, use_gpu=use_gpu)
        
        self.target_size = (640, 480)

    def process_frame(self, frame):
        """
        Processes a single video frame to detect obstacles and estimate their depth.

        Args:
            frame (np.ndarray): The input video frame in BGR format (from OpenCV).

        Returns:
            np.ndarray: A 2D grid where each cell contains the average depth of a detected obstacle.
                        Non-obstacle cells will have a value of np.nan.
        """
        # 1. Preprocess the frame
        frame_resized = cv2.resize(frame, self.target_size)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)

        # 2. Get depth map and obstacle grid
        depth_pil = self.depth_processor.infer_pil(image)
        depth_np = np.array(depth_pil)
        # Flip the depth inside out
        min_d, max_d = np.nanmin(depth_np), np.nanmax(depth_np)
        flipped_depth_np = max_d + min_d - depth_np
        output_obstacles = self.obstacle_grid_model(frame_resized)

        # 3. Combine depth and obstacle information
        h, w = flipped_depth_np.shape
        grid_h, grid_w = output_obstacles.shape[:2]
        cell_h, cell_w = h / grid_h, w / grid_w

        obstacle_depth_map = np.full((grid_h, grid_w), np.nan, dtype=np.float32)

        for i in range(grid_h):
            for j in range(grid_w):
                # Check if the cell is an obstacle (assuming channel 0 has the obstacle probability)
                if output_obstacles[i, j, 0] > 0.5:
                    # Define the region in the depth map corresponding to this grid cell
                    y1, y2 = int(i * cell_h), int((i + 1) * cell_h)
                    x1, x2 = int(j * cell_w), int((j + 1) * cell_w)
                    
                    # Extract the depth values for the cell
                    depth_cell = flipped_depth_np[y1:y2, x1:x2]
                    
                    # Only compute mean if the region is non-empty
                    if depth_cell.size > 0:
                        cell_depth = np.nanmean(depth_cell)
                        if not np.isnan(cell_depth):
                            obstacle_depth_map[i, j] = cell_depth
        
        return obstacle_depth_map
    
    def visualize_obstacles(self, frame, obstacle_depth_map):
        """
        Visualizes the detected obstacles on the input frame.
        Opens a matplotlib window to display the frame with obstacles highlighted.

        Args:
            frame (np.ndarray): The input video frame in BGR format.
            obstacle_depth_map (np.ndarray): The 2D grid of obstacle depths.

        Returns:
            None
        """

        # Prepare frame and depth map for visualization
        frame_resized = cv2.resize(frame, self.target_size)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]

        # For visualization, we need the depth map and obstacle grid
        # We'll re-run the models here for demonstration, but ideally pass them in
        image = Image.fromarray(frame_rgb)
        depth_pil = self.depth_processor.infer_pil(image)
        depth_np = np.array(depth_pil)
        # Flip the depth inside out
        min_d, max_d = np.nanmin(depth_np), np.nanmax(depth_np)
        flipped_depth_np = max_d + min_d - depth_np
        output_obstacles = self.obstacle_grid_model(frame_resized)

        grid_h, grid_w = output_obstacles.shape[:2]
        cell_h, cell_w = h / grid_h, w / grid_w

        # Create figure and axes
        fig = plt.figure(figsize=(18, 6))
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2, projection='3d')
        ax3 = fig.add_subplot(1, 3, 3, projection='3d')

        # Plot original frame with obstacle rectangles
        ax1.set_title("Original Frame")
        ax1.imshow(frame_rgb)
        ax1.axis('off')
        for i in range(grid_h):
            for j in range(grid_w):
                if output_obstacles[i, j, 0] > 0.5:
                    y1, y2 = int(i * cell_h), int((i + 1) * cell_h)
                    x1, x2 = int(j * cell_w), int((j + 1) * cell_w)
                    # Use flipped depth
                    depth_cell = flipped_depth_np[y1:y2, x1:x2]
                    if depth_cell.size > 0:
                        cell_depth = np.nanmean(depth_cell)
                        min_d, max_d = np.nanmin(flipped_depth_np), np.nanmax(flipped_depth_np)
                        if not np.isnan(cell_depth) and (max_d - min_d) > 0:
                            norm_depth = (cell_depth - min_d) / (max_d - min_d)
                            alpha = 0.9 * (1 - norm_depth)
                            rect = Rectangle((x1, y1), x2-x1, y2-y1, linewidth=1, edgecolor='red', facecolor='none', alpha=alpha)
                            ax1.add_patch(rect)

        # Plot depth map as 3D surface
        ax2.set_title("Depth Map (3D Surface, Flipped)")
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        # Resize depth_np to match (h, w) for plotting
        depth_np_resized = cv2.resize(flipped_depth_np, (w, h), interpolation=cv2.INTER_LINEAR)
        ax2.plot_surface(x, y, depth_np_resized, cmap='viridis', edgecolor='none', alpha=0.7)
        ax2.set_xlabel("Width")
        ax2.set_ylabel("Height")
        ax2.set_zlabel("Depth")
        ax2.view_init(elev=290, azim=-90)

        # Plot obstacles as red squares in 3D
        ax3.set_title("Obstacles (Red Squares, 3D, Flipped)")
        xs, ys, zs = [], [], []
        for i in range(grid_h):
            for j in range(grid_w):
                if output_obstacles[i, j, 0] > 0.5:
                    y1, y2 = int(i * cell_h), int((i + 1) * cell_h)
                    x1, x2 = int(j * cell_w), int((j + 1) * cell_w)
                    # Use flipped depth
                    depth_cell = flipped_depth_np[y1:y2, x1:x2]
                    if depth_cell.size > 0:
                        cell_depth = np.nanmean(depth_cell)
                        if not np.isnan(cell_depth):
                            xs.append((x1 + x2) / 2)
                            ys.append((y1 + y2) / 2)
                            zs.append(cell_depth)
        if len(xs) > 0:
            ax3.scatter(xs, ys, zs, color='red', s=100, edgecolors='black')
        ax3.set_xlabel("Width")
        ax3.set_ylabel("Height")
        ax3.set_zlabel("Depth")
        ax3.set_xlim(0, w)
        ax3.set_ylim(0, h)
        ax3.set_zlim(np.nanmin(flipped_depth_np), np.nanmax(flipped_depth_np))
        ax3.view_init(elev=290, azim=-90)

        plt.tight_layout()
        plt.show()
        
if __name__ == '__main__':
    # Example usage:
    # This part demonstrates how to use the ObstacleDetector class.
    # It reads from a sample video, processes each frame, and prints the result.

    # --- Configuration ---
    video_path = "/home/ali/codebases/AvoidNet/samples/underwater_drone_sample.mp4"
    vizualize = True  # Set to True if you want to visualize the obstacles
    
    # --- Initialization ---
    detector = ObstacleDetector()
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        exit()

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing video with {total_frames} frames...")

    # --- Processing Loop ---
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame
        obstacle_map = detector.process_frame(frame)
        if vizualize:
            detector.visualize_obstacles(frame, obstacle_map)

        # --- Example: Print the output ---
        # For a real application, you would use this 'obstacle_map' for navigation,
        # visualization, etc. Here, we'll just print some info for the first few frames.
        if frame_count < 5:
            print(f"\n--- Frame {frame_count} ---")
            print("Obstacle Depth Map (NaN means no obstacle):")
            # Printing with precision for better readability
            with np.printoptions(precision=2, suppress=True, nanstr="."):
                print(obstacle_map)
        
        frame_count += 1
        
        # Optional: Add a simple progress indicator to the console
        if (frame_count % 10) == 0:
            print(f"Processed {frame_count}/{total_frames} frames...", end='\r')


    # --- Cleanup ---
    cap.release()
    print(f"\nFinished processing all {frame_count} frames.")