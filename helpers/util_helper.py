class UtilHelper:

    def cfDecodeEmail(encodedString):
        r = int(encodedString[:2], 16)
        email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r)
                        for i in range(2, len(encodedString), 2)])
        return email

    def log_to_file(file_name, text, variable):
        with open(file_name, 'a') as f:
            f.write(f"{text}+{variable}")
            f.write('\n')
