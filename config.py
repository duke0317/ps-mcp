# 图片处理MCP服务器配置文件

# 服务器配置
SERVER_NAME = "image-processor"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "基于MCP协议的图片处理服务器"

# 图片处理配置
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 最大图片大小 10MB
MIN_IMAGE_SIZE = 1    # 最小图片尺寸（像素）
SUPPORTED_FORMATS = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP', 'GIF']
DEFAULT_QUALITY = 85  # 默认图片质量
DEFAULT_FORMAT = 'PNG'  # 默认输出格式
DEFAULT_IMAGE_FORMAT = 'PNG'  # 默认图片格式（别名）

# 处理限制
MAX_DIMENSION = 4096  # 最大图片尺寸
MIN_DIMENSION = 1     # 最小图片尺寸
MAX_BLUR_RADIUS = 10.0
MAX_BRIGHTNESS_FACTOR = 2.0
MAX_CONTRAST_FACTOR = 2.0
MAX_SATURATION_FACTOR = 2.0
MAX_GAMMA_VALUE = 3.0

# 缓存配置
ENABLE_CACHE = False  # 是否启用缓存
CACHE_SIZE = 100      # 缓存大小
CACHE_TTL = 3600      # 缓存过期时间（秒）

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/image_processor.log"

# 安全配置
VALIDATE_INPUT = True   # 是否验证输入
SANITIZE_FILENAME = True  # 是否清理文件名
MAX_FILENAME_LENGTH = 255

# 性能配置
ENABLE_ASYNC_PROCESSING = True  # 是否启用异步处理
MAX_CONCURRENT_TASKS = 4  # 最大并发任务数
PROCESSING_TIMEOUT = 30  # 处理超时时间（秒）
ENABLE_CACHE = True  # 是否启用缓存
CACHE_SIZE_MB = 100  # 缓存大小（MB）

# 批量处理配置
MAX_BATCH_SIZE = 20  # 最大批量处理数量
BATCH_TIMEOUT = 60  # 批量处理超时时间（秒）

# 特效处理配置
MAX_BORDER_WIDTH = 100  # 最大边框宽度
MAX_SHADOW_BLUR = 50  # 最大阴影模糊半径
MAX_WATERMARK_SCALE = 1.0  # 最大水印缩放比例
MIN_WATERMARK_SCALE = 0.1  # 最小水印缩放比例

# GIF创建配置
MAX_GIF_FRAMES = 50  # 最大GIF帧数
MIN_GIF_DURATION = 50  # 最小帧持续时间（毫秒）
MAX_GIF_DURATION = 10000  # 最大帧持续时间（毫秒）
MAX_GIF_SIZE = 10 * 1024 * 1024  # 最大GIF文件大小（字节）

# 拼贴配置
MAX_COLLAGE_IMAGES = 25  # 最大拼贴图片数量
MAX_COLLAGE_SIZE = 4096  # 最大拼贴尺寸

# 颜色提取配置
MAX_EXTRACT_COLORS = 50  # 最大提取颜色数量
MIN_EXTRACT_COLORS = 1  # 最小提取颜色数量

# 输出模式配置
OUTPUT_MODE = "file_ref"  # 默认使用文件引用模式
TEMP_DIR = "temp"  # 临时文件目录
USE_OPERATION_PREFIX = True  # 文件名是否使用操作前缀

# 开发配置
DEBUG_MODE = False
VERBOSE_ERRORS = True  # 是否显示详细错误信息