import tensorflow as tf


NUM_FRAMES = 60
NUM_JOINTS = 7
STATE_DIM = 3
IMG_WIDTH = 224
IMG_HEIGHT = 224
COLOR_CHANNELS = 3


def read_tf_record(data_path):
    #gets data path
    # data_path = FLAGS.data_path

    #setup tf session
    # with tf.Session() as sess:
        #feature dictionary definition
    feature = {
        'train/image': tf.FixedLenFeature([IMG_WIDTH * IMG_HEIGHT * NUM_FRAMES * 3], tf.string),
        'train/angle': tf.FixedLenFeature([NUM_JOINTS * NUM_FRAMES], tf.float32),
        'train/velocity': tf.FixedLenFeature([NUM_JOINTS * NUM_FRAMES], tf.float32),
        'train/endeffector_pos': tf.FixedLenFeature([STATE_DIM * NUM_FRAMES], tf.float32),
    }


    # Create a list of filenames and pass it to a queue
    filename_queue = tf.train.string_input_producer([data_path], num_epochs=1)
    # Define a reader and read the next record
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    # Decode the record read by the reader
    features = tf.parse_single_example(serialized_example, features=feature)


    # Convert the image and robot data from string back to the numbers
    image = tf.decode_raw(features['train/image'], tf.uint8)
    angle = tf.reshape(features['train/angle'], shape=[NUM_FRAMES, NUM_JOINTS])
    velocity = tf.reshape(features['train/velocity'], shape=[NUM_FRAMES, NUM_JOINTS])
    endeffector_pos = tf.reshape(features['train/endeffector_pos'], shape=[NUM_FRAMES, STATE_DIM])

    # Reshape image data into original video
    image = tf.reshape(image, [NUM_FRAMES, IMG_HEIGHT, IMG_WIDTH, COLOR_CHANNELS])


    # Creates batches by randomly shuffling tensors. each training example is (image,velocity) pair
    images, angles, velocities, endeffector_poses = tf.train.shuffle_batch([image, angle, velocity, endeffector_pos], batch_size=32, capacity=1800, num_threads=1, min_after_dequeue=1200, enqueue_many=True)

    return images, angles, velocities, endeffector_poses


def main():
    from tensorflow.python.platform import flags

    FLAGS = flags.FLAGS
    flags.DEFINE_string('data_path', './', 'path to tfrecords file')

    import cv2
        # # Initialize all global and local variables
    with tf.Session(config = tf.ConfigProto(
        device_count = {'GPU': 0}
    )) as sess:
        images, angles, velocities, endeffector_poses = read_tf_record(FLAGS.data_path)

        init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        sess.run(init_op)
        # # Create a coordinator and run all QueueRunner objects
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        #
        for batch_index in range(5):

            img, vel, ef, ang = sess.run([images, velocities, endeffector_poses, angles])

            print 'vel', vel.shape
            print 'ef', ef.shape
            print 'ang', ang.shape
            for i in range(15):
                cv2.imshow('img', img[i])
                cv2.waitKey(0)

    #     # Stop the threads
        coord.request_stop()
    #
    #     # Wait for threads to stop
    #     coord.join(threads)
    sess.close()

if __name__ == '__main__':
    main()