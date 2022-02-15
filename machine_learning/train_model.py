from pathlib import Path
from PIL import Image

from pycoral.adapters import classify
from pycoral.adapters import common
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from pycoral.learn.imprinting.engine import ImprintingEngine

def contents(folder):
    for filename in folder.iterdir():
        yield folder/filename

script_dir = Path(__file__).parent.resolve()
print (script_dir.name)
model_path = script_dir/'models'/'module.tflite'
out_model_path = script_dir/'models'/'astropi-day-vs-nite.tflite'
data_dir = script_dir/'data'
labels_path = data_dir/'day-vs-night.txt'

engine = ImprintingEngine(f"{model_path}", keep_classes=False)

extractor_interpreter = make_interpreter(engine.serialize_extractor_model())
extractor_interpreter.allocate_tensors()
size = common.input_size(extractor_interpreter)

labels = read_label_file(labels_path)


for class_id, class_name in labels.items():
    print(f"{class_id}: {class_name}")

    for image_path in contents(data_dir/class_name):
        image = Image.open(image_path).convert('RGB').resize(size, Image.NEAREST)
        common.set_input(extractor_interpreter, image)
        extractor_interpreter.invoke()
        embedding = classify.get_scores(extractor_interpreter)
        print(f"{image_path.name} scores: {embedding}")
        engine.train(embedding, class_id)

with open(out_model_path, 'wb') as f:
    f.write(engine.serialize_model())





