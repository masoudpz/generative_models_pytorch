import argparser
import dataloader
import model
import torch.optim as optim
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.distributions
from torchvision.utils import save_image
from tensorboardX import SummaryWriter

parser = argparser.default_parser()
parser.add_argument('--log-directory', type=str, default='/home/sungwonlyu/experiment/dcgan', metavar='N',
                    help='log directory')

args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

writer = SummaryWriter(args.log_directory + '/' + args.time_stamp + '/')

torch.manual_seed(args.seed)
if args.cuda:
    torch.cuda.manual_seed(args.seed)

train_loader = dataloader.train_loader('mnist', args.data_directory, args.batch_size)

if args.load_model != '000000':
    discriminator = torch.load(args.log_directory + '/' + args.load_model + '/discriminator.pt')
    generator = torch.load(args.log_directory + '/' + args.load_model + '/generator.pt')
else:
    discriminator = model.Discriminator()
    generator = model.Generator()

if args.cuda:
    discriminator.cuda()
    generator.cuda()

discriminator_optimizer = optim.Adam(discriminator.parameters(), lr=args.lr, betas = (0.5, 0.999))
generator_optimizer = optim.Adam(generator.parameters(), lr=args.lr, betas = (0.5, 0.999))
loss_function = nn.BCELoss()

def train(epoch):
    train_loss = 0
    discriminator.train()
    generator.train()
    for batch_idx, (input_data, label) in enumerate(train_loader):
        discriminator_optimizer.zero_grad()
        generator_optimizer.zero_grad()
        noise = torch.rand(len(input_data), 100)
        input_data = (input_data - 0.5) * 2
        noise = Variable(noise)
        input_data = Variable(input_data)
        if args.cuda:
            noise = noise.cuda()
            input_data = input_data.cuda()
        fake = generator(noise)
        real_likelihood = discriminator(input_data)
        fake_likelihood = discriminator(fake.detach())
        dis_loss = loss_function(real_likelihood, torch.ones_like(real_likelihood)) + loss_function(fake_likelihood, torch.zeros_like(fake_likelihood))
        dis_loss /= 2
        # dis_loss = - (torch.sum(torch.log(real_likelihood) + torch.log(1 - fake_likelihood)))
        # gen_loss = -torch.sum(torch.log(fake_likelihood))
        dis_loss.backward()
        discriminator_optimizer.step()

        fake_likelihood = discriminator(fake)
        gen_loss = loss_function(fake_likelihood, torch.ones_like(fake_likelihood))
        gen_loss.backward()
        generator_optimizer.step()

        writer.add_scalar('gen loss', gen_loss, epoch * len(train_loader) + batch_idx)
        writer.add_scalar('dis loss', dis_loss, epoch * len(train_loader) + batch_idx)
        loss = (gen_loss + dis_loss)
        train_loss += loss.data
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * args.batch_size, len(train_loader.dataset),
                       100. * batch_idx / len(train_loader),
                loss.data))
    print('====> Epoch: {} Average loss: {:.4f}'.format(
        epoch, train_loss / len(train_loader)))


def sample():
    generator.eval()
    noise = torch.rand(8, 100)
    noise = Variable(noise)
    if args.cuda:
        noise = noise.cuda()
    sample = generator(noise)
    sample = sample / 2 + 0.5
    save_image(sample.data, 'results/sample_' + str(epoch) + '.png')
    writer.add_image('Sample Image', sample.data, epoch)


for epoch in range(args.epochs):
    train(epoch)
    sample()

torch.save(discriminator, args.log_directory + '/' + args.time_stamp + '/discriminator.pt')
torch.save(generator, args.log_directory + '/' + args.time_stamp + '/generator.pt')
print('Model saved in ', args.log_directory + '/' + args.time_stamp + '/discriminator.pt')
print('Model saved in ', args.log_directory + '/' + args.time_stamp + '/generator.pt')
writer.close()
