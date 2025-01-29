import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import random  # For random number generation
import colorsys  # For hue adjustment


class ImageProcessingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Settings")

        # Check if the "images" folder exists in the current directory
        self.images_folder = os.path.join(os.getcwd(), "images")
        if not os.path.exists(self.images_folder):
            try:
                os.mkdir(self.images_folder)  # Create folder if it doesn't exist
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create 'images' folder: {e}")
                return

        # Load images from the "images" folder
        self.load_images()

        # Define variables for checkboxes
        self.blur_var = tk.BooleanVar()
        self.contrast_var = tk.BooleanVar()
        self.gamma_var = tk.BooleanVar()
        self.brightness_var = tk.BooleanVar()  # For brightness adjustment
        self.hue_var = tk.BooleanVar()  # For hue adjustment
        self.saturation_var = tk.BooleanVar()  # For saturation adjustment
        self.noise_var = tk.BooleanVar()  # For Gaussian Noise

        # Blur checkbox
        self.blur_check = tk.Checkbutton(root, text="Apply Blur", variable=self.blur_var)
        self.blur_check.grid(row=0, column=0, sticky='w')

        # Contrast checkbox
        self.contrast_check = tk.Checkbutton(root, text="Adjust Contrast", variable=self.contrast_var)
        self.contrast_check.grid(row=1, column=0, sticky='w')

        # Random Gamma checkbox
        self.gamma_check = tk.Checkbutton(root, text="Apply Random Gamma", variable=self.gamma_var)
        self.gamma_check.grid(row=2, column=0, sticky='w')

        # Brightness checkbox
        self.brightness_check = tk.Checkbutton(root, text="Adjust Brightness", variable=self.brightness_var)
        self.brightness_check.grid(row=3, column=0, sticky='w')

        # Hue checkbox
        self.hue_check = tk.Checkbutton(root, text="Adjust Hue [Capped at 1.0]", variable=self.hue_var)
        self.hue_check.grid(row=4, column=0, sticky='w')

        # Saturation checkbox
        self.saturation_check = tk.Checkbutton(root, text="Adjust Saturation", variable=self.saturation_var)
        self.saturation_check.grid(row=5, column=0, sticky='w')

        # Gaussian Noise checkbox
        self.noise_check = tk.Checkbutton(root, text="Apply Gaussian Noise", variable=self.noise_var)
        self.noise_check.grid(row=6, column=0, sticky='w')

        # Label for input ranges
        self.range_label = tk.Label(root, text="Input Range (0.1 - 5.0):")
        self.range_label.grid(row=7, column=0, sticky='w')

        # Entry widgets for user input ranges
        self.range_entry = tk.Entry(root)
        self.range_entry.grid(row=7, column=1)
        self.range_entry.insert(0, "1.0")  # default value

        # Apply button
        self.apply_button = tk.Button(root, text="Apply Settings", command=self.apply_settings)
        self.apply_button.grid(row=8, column=0, columnspan=2)

    def load_images(self):
        # Try to load images from the "images" folder
        try:
            self.image_files = [f for f in os.listdir(self.images_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            if self.image_files:
                print(f"Found images: {self.image_files}")
            else:
                print("No images found in the 'images' folder.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {e}")

    def apply_settings(self):
        # Retrieve the current state of checkboxes and entry value
        blur = self.blur_var.get()
        contrast = self.contrast_var.get()
        gamma = self.gamma_var.get()
        brightness = self.brightness_var.get()
        hue = self.hue_var.get()
        saturation = self.saturation_var.get()
        noise = self.noise_var.get()
        input_range = self.range_entry.get()

        try:
            input_range = float(input_range)
            if not (0.1 <= input_range <= 5.0):  # Updated maximum range to 5.0
                raise ValueError("Input range must be between 0.1 and 5.0")
        except ValueError as e:
            print(f"Invalid range: {e}")
            return

        # Create a new folder to save augmented images in the root directory
        augmented_folder = os.path.join(os.getcwd(), "Augmented_images")
        if not os.path.exists(augmented_folder):
            os.mkdir(augmented_folder)

        # Apply augmentations to each image
        for image_file in self.image_files:
            image_path = os.path.join(self.images_folder, image_file)
            image = Image.open(image_path)

            # Save the original image
            original_image_path = os.path.join(self.images_folder, f"original_{image_file}")
            self.save_image(image, original_image_path)

            # Create a copy of the image for processing
            processed_image = image.copy()

            # Apply Blur
            if blur:
                processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=input_range))

            # Apply Random Contrast
            if contrast:
                processed_image = self.apply_random_contrast(processed_image, input_range)

            # Apply Random Brightness
            if brightness:
                processed_image = self.apply_random_brightness(processed_image, input_range)

            # Apply Random Gamma (adjust brightness)
            if gamma:
                processed_image = self.apply_random_gamma(processed_image, input_range)

            # Apply Hue adjustment
            if hue:
                processed_image = self.apply_hue(processed_image, input_range)

            # Apply Saturation adjustment
            if saturation:
                processed_image = self.apply_saturation(processed_image, input_range)

            # Apply Gaussian Noise
            if noise:
                processed_image = self.apply_gaussian_noise(processed_image)

            # Save the processed image
            new_image_path = os.path.join(augmented_folder, f"{os.path.splitext(image_file)[0]}_augmented{os.path.splitext(image_file)[1]}")
            self.save_image(processed_image, new_image_path)

            print(f"Processed and saved: {new_image_path}")

    def save_image(self, image, image_path):
        # Save the image in its original mode (no mode conversion)
        if image.mode == 'RGBA':
            image.save(image_path, format='PNG')
        else:
            if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                image.save(image_path, format='JPEG')
            else:
                image.save(image_path, format='PNG')

    def apply_random_contrast(self, image, contrast_factor):
        factor = random.uniform(0.1, contrast_factor)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def apply_random_brightness(self, image, brightness_factor):
        factor = random.uniform(0.1, brightness_factor)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def apply_random_gamma(self, image, gamma_value):
        image_array = np.array(image)
        gamma_corrected = np.power(image_array / float(np.max(image_array)), gamma_value) * 255.0
        gamma_corrected = np.uint8(np.clip(gamma_corrected, 0, 255))
        return Image.fromarray(gamma_corrected)

    def apply_hue(self, image, hue_factor):
        image_hsv = image.convert("HSV")
        h, s, v = np.array(image_hsv).T
        h = (h + int(hue_factor * 255)) % 255
        image_hsv = Image.fromarray(np.array([h, s, v]).T, "HSV")
        return image_hsv.convert("RGB")

    def apply_saturation(self, image, saturation_factor):
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(saturation_factor)

    def apply_gaussian_noise(self, image):
        image_array = np.array(image)
        mean = 0
        std = 25
        noise = np.random.normal(mean, std, image_array.shape).astype(np.uint8)
        noisy_image = np.clip(image_array + noise, 0, 255)
        return Image.fromarray(noisy_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingGUI(root)
    root.mainloop()
