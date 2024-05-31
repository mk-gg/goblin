import sys


from src.config import *
from src.utils import *



load_config()


if __name__ == '__main__':

    try:
        print(" Hello World!")
    
    except KeyboardInterrupt:
        pass

    except Exception as e:
        
        print(f'Exception while connecting: {str(e).rstrip()}')
    
    sys.exit('\nClosing.')