import torch
from torch import nn
import torch.nn.functional as F

class Encoder(nn.Module):
    def __init__(self, input_h=280, input_w=420, hidden_size = 400, latent_size = 10):
        super(Encoder, self).__init__()
        self.input_h = input_h
        self.input_w = input_w
        self.hidden_size = hidden_size
        self.latent_size = latent_size
        self.fc1 = nn.Linear(input_h * input_w, hidden_size * 2)
        self.fc2 = nn.Linear(hidden_size * 2, hidden_size)
        self.fc3 = nn.Linear(hidden_size, latent_size * 2)
        torch.nn.init.normal_(self.fc1.weight, 0, 0.01)
        torch.nn.init.normal_(self.fc2.weight, 0, 0.01)
        torch.nn.init.normal_(self.fc3.weight, 0, 0.01)

    def forward(self, x):
        x = x.view(-1, self.input_h * self.input_w)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x = x.view(-1, 2, self.latent_size)
        return x

class Decoder(nn.Module):
    def __init__(self, output_h=280, output_w=420, hidden_size = 400, latent_size = 10):
        super(Decoder, self).__init__()
        self.output_h = output_h
        self.output_w = output_w
        self.hidden_size = hidden_size
        self.latent_size = latent_size
        self.fc1 = nn.Linear(latent_size, hidden_size * 2)
        self.fc2 = nn.Linear(hidden_size * 2, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_h * output_w)
        torch.nn.init.normal_(self.fc1.weight, 0, 0.01)
        torch.nn.init.normal_(self.fc2.weight, 0, 0.01)
        torch.nn.init.normal_(self.fc3.weight, 0, 0.01)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.sigmoid(self.fc3(x))
        return x.view(-1, 1, self.output_h, self.output_w)