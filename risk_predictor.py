import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras import optimizers

from constants import TILE


# ── Neural Network Risk Predictor & Hyperparameter Optimization ───────────────
class RiskPredictor:
    def __init__(self):
        self.model = None
        self.best_lr = None
        self._train()

    def _generate_dataset(self):
        X, Y = [], []
        for dx in range(-15, 16):
            for dy in range(-15, 16):
                dist = abs(dx) + abs(dy)
                X.append([dx, dy])
                if dist <= 3:
                    Y.append([0, 1])  # Risky
                else:
                    Y.append([1, 0])  # Safe
        return np.array(X), np.array(Y)

    def _evaluate_nn(self, lr, X, Y):
        """Trains a model with a given learning rate and returns training loss."""
        # Memory cleanup to prevent RAM overload during Hill Climbing loop
        tf.keras.backend.clear_session()

        model = Sequential()
        model.add(Dense(16, input_dim=2))
        model.add(Activation('relu'))
        model.add(Dense(8))
        model.add(Activation('relu'))
        model.add(Dense(2))
        model.add(Activation('softmax'))

        # Using SGD optimizer as required
        model.compile(loss='categorical_crossentropy', optimizer=optimizers.SGD(learning_rate=lr), metrics=['accuracy'])
        history = model.fit(X, Y, batch_size=64, epochs=10, verbose=0)
        # Return the final loss (we want to minimize this)
        return history.history['loss'][-1]

    def _train(self):
        print("Generating dataset for Neural Network...")
        X, Y = self._generate_dataset()

        print("Running Local Search (Hill Climbing) to find optimal learning rate...")
        # Using the Hill Climbing logic (simple discrete space)
        available_lrs = [0.001, 0.01, 0.05, 0.1, 0.2]
        best_lr = available_lrs[0]
        best_loss = self._evaluate_nn(best_lr, X, Y)

        for lr in available_lrs[1:]:
            loss = self._evaluate_nn(lr, X, Y)
            if loss < best_loss:
                best_loss = loss
                best_lr = lr

        print(f"Optimal learning rate found: {best_lr} (Loss: {best_loss:.4f})")
        self.best_lr = best_lr

        print("Training Final Neural Network Model...")
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=2))
        self.model.add(Activation('relu'))
        self.model.add(Dense(8))
        self.model.add(Activation('relu'))
        self.model.add(Dense(2))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer=optimizers.SGD(learning_rate=best_lr), metrics=['accuracy'])
        self.model.fit(X, Y, batch_size=64, epochs=30, verbose=0)
        print("Neural Network Ready.")

    def get_risk_percentage(self, cell, enemies):
        """Predict risk probability (0-100) from local features using the Neural Network."""
        cx, cy = cell
        if not enemies:
            return 0.0

        closest_en = None
        min_dist = float('inf')
        for en in enemies:
            ex, ey = int(en['pos'][0]//TILE), int(en['pos'][1]//TILE)
            dist = abs(cx-ex) + abs(cy-ey)
            if dist < min_dist:
                min_dist = dist
                closest_en = (ex, ey)

        if closest_en is None:
            return 0.0

        dx = cx - closest_en[0]
        dy = cy - closest_en[1]

        # OPTIMIZATION: Use direct tensor call instead of .predict() for real-time 60FPS loop to stop lag
        pred = self.model(np.array([[dx, dy]]), training=False)[0].numpy()
        return float(pred[1] * 100)  # Index 1 corresponds to the 'Risky' class
