import argparse
from pathlib import Path

import tensorflow as tf


def convert(input_path: str, output_path: str, quantize: str):
    model = tf.keras.models.load_model(input_path, compile=False)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if quantize in {"dynamic", "int8"}:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if quantize == "float16":
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]

    if quantize == "int8":
        # Dynamic range quantization keeps float input/output and is safe
        # without a calibration dataset. Full integer quantization should be
        # added later only with a representative face dataset.
        print("Using dynamic int8 weight quantization with float input/output.")

    tflite_model = converter.convert()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(tflite_model)
    print(f"Wrote {output} ({len(tflite_model) / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="models/cnn_v3_final.h5")
    parser.add_argument("--output", default="models/cnn_v3_final.tflite")
    parser.add_argument(
        "--quantize",
        choices=["none", "dynamic", "float16", "int8"],
        default="dynamic",
    )
    args = parser.parse_args()
    convert(args.input, args.output, args.quantize)


if __name__ == "__main__":
    main()
