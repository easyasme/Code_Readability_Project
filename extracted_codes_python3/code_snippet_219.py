from keras.callbacks import EarlyStopping
from keras.metrics import AUC
from keras.optimizers import Adam

from build_model import ModelBuilder


class ModelTrainer:

    def __init__(self, learning_rate=1e-3, epochs=1000,
                 batch_size=128, layers=2,
                 units=64, dropout_rate=0.2):
        self._learning_rate = learning_rate
        self._epochs = epochs
        self._batch_size = batch_size
        self._layers = layers
        self._units = units
        self._dropout_rate = dropout_rate

    def train(self, data):
        # Get the data.
        (x_train, y_train), (x_val, y_val) = data

        # Create model instance.
        builder = ModelBuilder(layers=self._layers, units=self._units,
                               dropout_rate=self._dropout_rate,
                               input_shape=x_train.shape[1:])

        model = builder.build()

        # Compile model with learning parameters.
        loss = 'binary_crossentropy'
        optimizer = Adam(lr=self._learning_rate)

        # Accuracy and AUC metrics
        model.compile(optimizer=optimizer, loss=loss, metrics=['acc', AUC()])

        # Create callback for early stopping on validation loss. If the loss
        # does not decrease in three consecutive tries, stop training.
        callbacks = [EarlyStopping(monitor='val_loss', patience=3)]

        # Train and validate model.
        history = model.fit(
            x_train.toarray(),
            y_train,
            epochs=self._epochs,
            callbacks=callbacks,
            validation_data=(x_val.toarray(), y_val),
            verbose=0,
            batch_size=self._batch_size,
            shuffle=False
        )

        # Print results.
        history2 = history.history
        print('Validation accuracy: {acc}, loss: {loss}'.format(
            acc=history2['val_acc'][-1], loss=history2['val_loss'][-1]))

        # Save model.
        model.save('opcovidbr_mlp_model.h5')
        return history2['val_acc'][-1], history2['val_loss'][-1], history

    def set_params(self, learning_rate=1e-3, epochs=1000,
                 batch_size=128, layers=2,
                 units=64, dropout_rate=0.2):
        self._learning_rate = learning_rate
        self._epochs = epochs
        self._batch_size = batch_size
        self._layers = layers
        self._units = units
        self._dropout_rate = dropout_rate

    def get_params(self):
        params = dict()
        params['learning_rate'] = self._learning_rate
        params['epochs'] = self._epochs
        params['batch_size'] = self._batch_size
        params['layers'] = self._layers
        params['units'] = self._units
        params['dropout_rate'] = self._dropout_rate
        return params
