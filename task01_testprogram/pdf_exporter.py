from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


class PDFExporter:
    @staticmethod
    def export_to_pdf(figure, file_name):
        with PdfPages(file_name) as pdf:
            figure.savefig(pdf, format='pdf')
            plt.close()
