import numpy, random

class GeneratePrivateKey(object):

    def __init__(self):
        pass

    def generate_prime_number(self, n):
        # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
        """ Input n>=6, Returns a array of primes, 2 <= p < n """
        sieve = numpy.ones(n/3 + (n%6==2), dtype=numpy.bool)
        sieve[0] = False
        for i in xrange(int(n**0.5)/3+1):
            if sieve[i]:
                k=3*i+1|1
                sieve[      ((k*k)/3)      ::2*k] = False
                sieve[(k*k+4*k-2*k*(i&1))/3::2*k] = False
        return numpy.r_[2,3,((3*numpy.nonzero(sieve)[0]+1)|1)]

    def create_private_key(self, n):
        prime_to_n = self.generate_prime_number(n)
        prime_to_thousand = self.generate_prime_number(1000)
        thousand_length = len(prime_to_thousand)
        n_length = len(prime_to_n)
        private_keys = prime_to_n[thousand_length:n_length] # Removes prime numbers < 1000
        random_int = random.randint(0, len(private_keys))
        key = private_keys[random_int]
        return key

    def get_private_key(self):
        p = self.create_private_key(100000)
        q = self.create_private_key(100000)
        while q == p:
            q = self.create_private_key(100000)
        return long(p), long(q) # Return as long so they can be multiplied

    def store_private_key(self, p, q):
        a = [str(p), str(q)]
        f = open("private_key.txt", "w")
        f.write(', '.join(a))
        f.close()

class GeneratePublicKey(object):
    def __init__(self, p, q):
        self.p = p
        self.q = q

    # n = p * q
    def generate_n(self):
        n = self.p * self.q
        return n

    def generate_e(self):
        private_key = GeneratePrivateKey()
        prime_generator = private_key.create_private_key(10000)
        e = prime_generator
        phi_n = generate_phi_n(self.p, self.q)
        while phi_n % e == 0:
            e = prime_generator
        return long(e)

    def get_public_key(self):
        return self.generate_n(), self.generate_e()

    def store_public_key(self, n, e):
        a = [str(n), str(e)]
        f = open("public_key.txt", "w")
        f.write(', '.join(a))
        f.close()

class EncryptMessage(object):

    def __init__(self, n, e):
        self.n = n
        self.e = e

    def generate_hill_cipher_one(self, size):
        matrix = numpy.eye(size)
        for i in range(100):
            a = random.randint(0, size - 1)
            b = random.randint(0, size - 1)
            c = random.randint(1, 100)
            while b == a:
                b = random.randint(0, size - 1)
            matrix[a] = matrix[a] + c * matrix[b]
        return matrix

    def generate_hill_cipher_two(self, size):
        if size == 0:
            return [0]
        matrix = numpy.eye(size)      
        for i in range(100):
            a = random.randint(0, size - 1)
            b = random.randint(0, size - 1)
            c = random.randint(1, 100)
            while b == a:
                b = random.randint(0, size - 1)
            matrix[a] += c * matrix[b]
        return matrix

    def read_plain_text(self, file):
        f = open(file, "r")
        return f.read()
        f.close()

    def determine_matrix_sizes(self, text_length, size):
        if text_length / size == 0:  # Not enough to make one full-size matrix
            return text_length, 0
        elif text_length % size == 0:  # One matrix fits all
            return size, 0
        elif text_length % size == 1:
            if text_length / size == 1:  # ex/ size = 10, length = 11, so one 11x11 matrix
                return size + 1, 0
            else:                        # ex/ size = 10, length = 21
                return size, size + 1
        else:
            return size, text_length % size # ex output/ (10, 4)

    def number_of_matrices(self, text_length, size):
        if text_length % size == 1:  # ex/ 10 matrices for text_length = 100
            return text_length / size - 1
        else:
            return text_length / size

    def plain_text_to_number_text(self, plain_text):
        alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '.', ',', ';', '/', '?', '!', ':', '\'', '\"', '(', ')', '-', '_', '&', '%', '$', '#', '@',
            '[', ']', '{', '}', ' ', '\n', '*', '<', '>']
        number_text = []
        for i in range(len(plain_text)):
            if plain_text[i] in alphabet:
                number = alphabet.index(plain_text[i])
                number_text.append(number)
            else:
                number_text.append(86)
        return number_text

    def encrypt_plain_text(self, number_text, cipher1, cipher2, loops):
        encrypted_message = []
        for i in range(loops):
            array = []
            for j in range(len(cipher1[0])):
                array.append(number_text.pop(0))
            array2 = numpy.dot(array, cipher1)
            for i in range(len(array2)):
                encrypted_message.append(array2[i])
        if len(cipher2) != 1:
            array3 = []
            for i in range(len(number_text)):
                array3.append(number_text.pop(0))
            array4 = numpy.dot(array3, cipher2)
            for i in range(len(array4)):
                encrypted_message.append(array4[i])
        return encrypted_message

    def encrypt_cipher_with_public_key(self, cipher, n, e):
        if len(cipher) != 1:
            pk_encrypted_cipher = []
            for i in range(len(cipher[0])):
                array = cipher[i]
                for j in range(len(cipher[0])):
                    m = long(array[j])
                    c = (m ** e) % n
                    pk_encrypted_cipher.append(c)
            return pk_encrypted_cipher
        else:
            return []

    def encrypt_message_with_public_key(self, message, n, e):
        pk_encrypted_message = []
        for i in range(len(message)):
            m = long(message[i])
            c = m ** e % n
            pk_encrypted_message.append(c)
        return pk_encrypted_message

    def matrix_to_string(self, send_file, size, cipher):
        for i in range(size ** 2):
            send_file = send_file + str(cipher[i]) + "."
        return send_file

    def create_encrypted_string(self, size_one, size_two, cipher_one, cipher_two, message):
        send_file = str(size_one) + "." + str(size_two) + "."
        send_file = self.matrix_to_string(send_file, size_one, cipher_one)
        send_file = self.matrix_to_string(send_file, size_two, cipher_two)
        for i in range(len(message)):
            send_file = send_file + str(message[i]) + "."
        return send_file

    def output_encrypted_message(self, encrypted_string):
        f = open("encrypted_message.txt", "w")
        f.write(encrypted_string)
        f.close()



class DecryptMessage(object):
    def __init__(self, textfile, p, q, e):
        self.textfile = textfile
        self.p = p
        self.q = q
        self.e = e
        self.n = p * q

    def read_encrypted_text(self):
        f = open(self.textfile, "r")
        return f.read()
        f.close()

    def separate_matrix_from_message(self, encrypted_message):
        encrypted_array = encrypted_message.split(".")
        encrypted_array.pop()
        size_one = int(encrypted_array.pop(0))
        size_two = int(encrypted_array.pop(0))
        matrix_length_one = size_one ** 2
        matrix_length_two = size_two ** 2
        matrix_one = []
        for i in range(matrix_length_one):
            matrix_one.append(encrypted_array.pop(0))
        matrix_two = []
        for i in range(matrix_length_two):
            matrix_two.append(encrypted_array.pop(0))
        message = encrypted_array
        print matrix_one
        print matrix_two
        return matrix_one, matrix_two, message, size_one, size_two

    def generate_d(self, phi_n):
        a = 1
        while (a * phi_n + 1) % self.e != 0:
            a += 1
        d = (a * phi_n + 1) / self.e
        print d
        return d

    def decrypt_cipher(self, d, n, encrypted_cipher, size): # Cipher is c in the formula
        unencrypted_cipher = []
        for i in range(len(encrypted_cipher)):
            unencrypted_cipher.append((long(encrypted_cipher[i]) ** d) % n)
        matrix = []
        for i in range(size):
            matrix1 = unencrypted_cipher[10 * i, 10 * i + 10]
            matrix.append(matrix1)
        print matrix
        return matrix

    def invert_cipher(self, unencrypted_cipher):
        cipher = unencrypted_cipher
        return matrix(cipher).I

    def decrypt_pk_message(self, d, n, message):
        decrypted_message = []
        for i in range(len(message)):
            decrypted_message.append(long(message[i]) ** d % n)
        return decrypted_message

    def decrypt_hill_cipher(self, inverted_matrix1, inverted_matrix2, decrypted_message):
        size = len(inverted_matrix1[0])
        message = []
        loops = len(decrypted_message) / size
        for i in range(loops):
            array = []
            for j in range(size):
                array.append(decrypted_message.pop(0))
            message0 = numpy.dot(array, inverted_matrix1)
            for j in range(size):
                message.append(message0[j])
        size = len(inverted_matrix2[0])
        array1 = []
        for i in range(size):
            array1.append(decrypted_message.pop(0))
        array2 = numpy.dot(array1, inverted_matrix2)
        for i in range(size):
            message.append(array2[i])
        return message

    def message_to_plain_text(self, message):
        alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '.', ',', ';', '/', '?', '!', ':', '\'', '\"', '(', ')', '-', '_', '&', '%', '$', '#', '@',
            '[', ']', '{', '}', ' ', '\n', '*', '<', '>']
        plain_text = ""
        for i in range(len(message)):
                plain_text = plain_text + alphabet[message[i]]
        return plain_text

    def output_plain_text_message(self, message):
        f = open("decrypted_message.txt", "w")
        f.write(message)
        f.close()

# Helper methods

# phi(n) = (p - 1) * (q - 1)
def generate_phi_n(p, q):
    phi_n = (p - 1) * (q - 1)
    return phi_n

if __name__ == '__main__':
    a = GeneratePrivateKey()
    p, q = a.get_private_key()
    a.store_private_key(p, q)
    print str(p) + ", " + str(q)

    b = GeneratePublicKey(p, q)
    n, e = b.get_public_key()
    b.store_public_key(n, e)
    print str(n) + ", " + str(e)

    c = EncryptMessage(n, e)
    file = c.read_plain_text("test.txt")
    number_text = c.plain_text_to_number_text(file)
    text_length = len(number_text)
    number_of_matrices = c.number_of_matrices(text_length, 10)
    sizes = c.determine_matrix_sizes(len(file), 10)
    cipher_one = c.generate_hill_cipher_one(sizes[0])
    cipher_two = c.generate_hill_cipher_two(sizes[1])
    cipher_text = c.encrypt_plain_text(number_text, cipher_one, cipher_two, number_of_matrices)
    encrypted_cipher_one = c.encrypt_cipher_with_public_key(cipher_one, n, e)
    encrypted_cipher_two = c.encrypt_cipher_with_public_key(cipher_two, n, e)
    encrypted_message = c.encrypt_message_with_public_key(cipher_text, n, e)
    string = c.create_encrypted_string(sizes[0], sizes[1], encrypted_cipher_one, encrypted_cipher_two, encrypted_message)
    c.output_encrypted_message(string)

    dm = DecryptMessage("encrypted_message.txt", p, q, e)
    encrypted_message = dm.read_encrypted_text()
    matrices = dm.separate_matrix_from_message(encrypted_message)
    phi_n = generate_phi_n(p, q)
    d = dm.generate_d(phi_n)
    matrix1 = dm.decrypt_cipher(d, n, matrices[0], matrices[3])
    matrix2 = dm.decrypt_cipher(d, n, matrices[1], matrices[4])
    imatrix1 = dm.invert_cipher(matrix1)
    imatrix2 = dm.invert_cipher(matrix2)
    decrypted_message = dm.decrypt_pk_message(d, n, matrices[2])
    decrypted_hill_cipher = dm.decrypt_hill_cipher(imatrix1, imatrix2, decrypted_message)
    the_message = dm.message_to_plain_text(decrypted_hill_cipher)
    dm.output_plain_text_message(the_message)