"""
GAN-based procedural level generator.
Uses Generative Adversarial Network to create adaptive level layouts.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import json
from config.settings import MODEL_DIR, GAN_LATENT_DIM, LEVEL_WIDTH, TILE_SIZE


class Generator(nn.Module):
    """
    Generator network for creating level layouts.
    Transforms random noise into structured level data.
    """
    
    def __init__(self, latent_dim=100, output_dim=256):
        """
        Initialize generator.
        
        Args:
            latent_dim: Dimension of input noise vector
            output_dim: Dimension of output level representation
        """
        super(Generator, self).__init__()
        
        self.model = nn.Sequential(
            # Input layer
            nn.Linear(latent_dim, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            
            # Hidden layers
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(1024),
            
            nn.Linear(1024, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            
            # Output layer
            nn.Linear(512, output_dim),
            nn.Tanh()  # Output in range [-1, 1]
        )
    
    def forward(self, z):
        """
        Generate level from noise.
        
        Args:
            z: Random noise tensor
            
        Returns:
            Generated level representation
        """
        return self.model(z)


class Discriminator(nn.Module):
    """
    Discriminator network for evaluating level quality.
    Distinguishes real levels from generated ones.
    """
    
    def __init__(self, input_dim=256):
        """
        Initialize discriminator.
        
        Args:
            input_dim: Dimension of level representation
        """
        super(Discriminator, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(128, 1),
            nn.Sigmoid()  # Output probability [0, 1]
        )
    
    def forward(self, x):
        """
        Evaluate level.
        
        Args:
            x: Level representation
            
        Returns:
            Probability that level is real
        """
        return self.model(x)


class LevelGAN:
    """
    Complete GAN system for procedural level generation.
    Learns from template levels and generates new adaptive layouts.
    """
    
    def __init__(self, latent_dim=GAN_LATENT_DIM):
        """Initialize GAN system."""
        self.latent_dim = latent_dim
        self.output_dim = 256  # Encoded level representation
        
        # Device configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Initialize networks
        self.generator = Generator(latent_dim, self.output_dim).to(self.device)
        self.discriminator = Discriminator(self.output_dim).to(self.device)
        
        # Optimizers
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        # Loss function
        self.criterion = nn.BCELoss()
        
        # Training state
        self.is_trained = False
        
        # Try to load pre-trained model
        self.load_models()
    
    def load_models(self):
        """Load pre-trained GAN models if available."""
        gen_path = os.path.join(MODEL_DIR, 'level_generator.pth')
        disc_path = os.path.join(MODEL_DIR, 'level_discriminator.pth')
        
        try:
            if os.path.exists(gen_path) and os.path.exists(disc_path):
                self.generator.load_state_dict(torch.load(gen_path, map_location=self.device))
                self.discriminator.load_state_dict(torch.load(disc_path, map_location=self.device))
                self.is_trained = True
                print("Loaded pre-trained GAN models")
                return True
        except Exception as e:
            print(f"Could not load GAN models: {e}")
        
        return False
    
    def save_models(self):
        """Save trained GAN models."""
        try:
            os.makedirs(MODEL_DIR, exist_ok=True)
            
            gen_path = os.path.join(MODEL_DIR, 'level_generator.pth')
            disc_path = os.path.join(MODEL_DIR, 'level_discriminator.pth')
            
            torch.save(self.generator.state_dict(), gen_path)
            torch.save(self.discriminator.state_dict(), disc_path)
            
            print(f"GAN models saved to {MODEL_DIR}")
            
        except Exception as e:
            print(f"Error saving GAN models: {e}")
    
    def encode_level_template(self, platforms, coins, enemies):
        """
        Encode level components into vector representation.
        
        Args:
            platforms: List of platform objects
            coins: List of coin objects
            enemies: List of enemy objects
            
        Returns:
            Encoded level vector
        """
        # Create a simplified grid representation
        grid_width = self.output_dim // 16  # 16 rows
        grid_height = 16
        
        encoding = np.zeros((grid_height, grid_width))
        
        # Encode platforms
        for platform in platforms:
            grid_x = min(int(platform.x / TILE_SIZE) % grid_width, grid_width - 1)
            grid_y = min(int(platform.y / TILE_SIZE) % grid_height, grid_height - 1)
            encoding[grid_y, grid_x] = 0.5  # Platform marker
        
        # Encode coins
        for coin in coins:
            grid_x = min(int(coin.x / TILE_SIZE) % grid_width, grid_width - 1)
            grid_y = min(int(coin.y / TILE_SIZE) % grid_height, grid_height - 1)
            encoding[grid_y, grid_x] = 0.8  # Coin marker
        
        # Encode enemies
        for enemy in enemies:
            grid_x = min(int(enemy.x / TILE_SIZE) % grid_width, grid_width - 1)
            grid_y = min(int(enemy.y / TILE_SIZE) % grid_height, grid_height - 1)
            encoding[grid_y, grid_x] = -0.5  # Enemy marker
        
        # Flatten to vector
        return encoding.flatten()
    
    def decode_level_vector(self, level_vector, difficulty='intermediate'):
        """
        Decode vector representation into level components.
        
        Args:
            level_vector: Encoded level representation
            difficulty: Target difficulty level
            
        Returns:
            Dictionary with platforms, coins, enemies data
        """
        # Reshape vector to grid
        grid_height = 16
        grid_width = self.output_dim // grid_height
        
        grid = level_vector.reshape(grid_height, grid_width)
        
        platforms = []
        coins = []
        enemies = []
        
        # Threshold for detecting elements
        platform_threshold = 0.3
        coin_threshold = 0.6
        enemy_threshold = -0.3
        
        # Decode grid to level elements
        for y in range(grid_height):
            for x in range(grid_width):
                value = grid[y, x]
                
                world_x = x * TILE_SIZE * 2
                world_y = y * TILE_SIZE * 2
                
                if value > platform_threshold:
                    # Create platform
                    width = TILE_SIZE * 4
                    height = TILE_SIZE
                    platforms.append({
                        'x': world_x,
                        'y': world_y,
                        'width': width,
                        'height': height,
                        'type': 'normal'
                    })
                
                if value > coin_threshold:
                    coins.append({
                        'x': world_x,
                        'y': world_y
                    })
                
                if value < enemy_threshold:
                    enemies.append({
                        'x': world_x,
                        'y': world_y,
                        'type': 'walker'
                    })
        
        return {
            'platforms': platforms,
            'coins': coins,
            'enemies': enemies
        }
    
    def train(self, level_templates, epochs=100, batch_size=8):
        """
        Train GAN on level templates.
        
        Args:
            level_templates: List of encoded level templates
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        print(f"\nTraining GAN on {len(level_templates)} templates for {epochs} epochs...")
        
        # Convert templates to tensors
        real_data = torch.FloatTensor(np.array(level_templates)).to(self.device)
        
        for epoch in range(epochs):
            # Train Discriminator
            self.discriminator.zero_grad()
            
            # Real data
            real_labels = torch.ones(batch_size, 1).to(self.device)
            real_samples = real_data[torch.randint(0, len(real_data), (batch_size,))]
            real_output = self.discriminator(real_samples)
            d_loss_real = self.criterion(real_output, real_labels)
            
            # Fake data
            noise = torch.randn(batch_size, self.latent_dim).to(self.device)
            fake_samples = self.generator(noise)
            fake_labels = torch.zeros(batch_size, 1).to(self.device)
            fake_output = self.discriminator(fake_samples.detach())
            d_loss_fake = self.criterion(fake_output, fake_labels)
            
            # Total discriminator loss
            d_loss = d_loss_real + d_loss_fake
            d_loss.backward()
            self.d_optimizer.step()
            
            # Train Generator
            self.generator.zero_grad()
            
            noise = torch.randn(batch_size, self.latent_dim).to(self.device)
            fake_samples = self.generator(noise)
            fake_output = self.discriminator(fake_samples)
            g_loss = self.criterion(fake_output, real_labels)
            
            g_loss.backward()
            self.g_optimizer.step()
            
            # Log progress
            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - D Loss: {d_loss.item():.4f}, G Loss: {g_loss.item():.4f}")
        
        self.is_trained = True
        self.save_models()
        print("GAN training complete!")
    
    def generate_level(self, difficulty='intermediate', seed=None):
        """
        Generate a new level layout.
        
        Args:
            difficulty: Target difficulty (novice/intermediate/expert)
            seed: Optional random seed for reproducibility
            
        Returns:
            Dictionary with level components
        """
        self.generator.eval()
        
        with torch.no_grad():
            # Generate noise
            if seed is not None:
                torch.manual_seed(seed)
            
            noise = torch.randn(1, self.latent_dim).to(self.device)
            
            # Generate level
            generated = self.generator(noise)
            level_vector = generated.cpu().numpy()[0]
            
            # Decode to level components
            level_data = self.decode_level_vector(level_vector, difficulty)
            
        self.generator.train()
        
        return level_data
