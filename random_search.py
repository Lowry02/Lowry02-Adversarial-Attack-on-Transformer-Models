from utils.AdversarialAttack import AdversarialAttack
from utils.Logger import Logger
from utils.Chat import Chat
from argparse import ArgumentParser
import torch
import gc
import os

# random search algorithm
parser = ArgumentParser()
parser.add_argument("-m", "--model_name", dest="model_name", help="Model name to use")
parser.add_argument("-l", "--log_name", dest="log_name", help="Log file name")
parser.add_argument("-b", "--batch_size", dest="batch_size", help="Generator batch size", type=int, default=10)
args = parser.parse_args()
model_name = args.model_name
file_name = args.log_name
batch_size = args.batch_size

print(f"> RANDOM SEARCH[{model_name}]\n")
print("> Loading the model...")

log_folder = "log"
if log_folder not in os.listdir():
  os.mkdir(log_folder)
  
torch.cuda.empty_cache()

header = [
  "run",
  "iteration",
  "fitness",
  "sure_generated"
]
logger = Logger(header=header)
logger.create_file(f"./log/{file_name}.csv")

device = 'cuda'
quantized = False
chat = Chat(model_name, device=device, quantized=quantized)

population_size = 30
stop_criterion = 1000
adv_suffix_length = 25

print("> Attack starting...")

attacker = AdversarialAttack(
  chat=chat,
  logger=logger,
  population_size=population_size,
  stop_criterion=stop_criterion,
  adv_suffix_length=adv_suffix_length,
  batch_size=batch_size
)

attacker.run(method='rs')
logger.close_file()
gc.collect()
torch.cuda.empty_cache()

logger.header = ["run", "suffix"]
logger.create_file(f"./log/{file_name}-suffix.csv")
for index, suffix in enumerate(attacker.best_individuals):
  logger.log({"run": index + 1, "suffix": str(suffix.tolist()).replace(",", "|")})
logger.close_file()

print("> END")