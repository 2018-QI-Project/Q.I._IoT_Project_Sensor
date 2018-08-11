class BTError:
    ERR_UNKNOWN = -1
    ERR_NO_CMD = -2
    ERR_UNKNOWN_CMD = -3
    ERR_READ = -4
    ERR_WRITE = -5

    ERROR_MSG = {
        ERR_UNKNOWN: "Unknown error",
        ERR_NO_CMD: "No command given",
        ERR_UNKNOWN_CMD: "Unknown command"
    }

    @staticmethod
    def print_error(handler, error = -1, message = ""):
        if len(message) < 1:
            message = ERROR_MSG[error]

        print "ERROR {0}: {1}".format(error, message)
