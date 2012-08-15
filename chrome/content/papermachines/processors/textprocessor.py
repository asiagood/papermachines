#!/usr/bin/env python
import sys, os, csv, logging, tempfile, traceback, urllib

class TextProcessor:
	"""
	Base class for text processing in Paper Machines
	"""

	def __init__(self, sysargs, track_progress=True):
		logging.info("command: " + ' '.join([x.replace(' ','''\ ''') for x in sysargs]))
		self.cwd = sysargs[1]
		csv_file = sysargs[2]
		self.out_dir = sysargs[3]
		self.collection_name = sysargs[4]

		self.extra_args = sysargs[5:]

		self.collection = os.path.basename(csv_file).replace(".csv","")
		self.metadata = {}

		for rowdict in self.parse_csv(csv_file):
			filename = rowdict.pop("filename")
			self.metadata[filename] = rowdict

		self.files = self.metadata.keys()
		if track_progress:
			self.track_progress = True
			self.progress_initialized = False


	def parse_csv(self, filename, dialect=csv.excel, **kwargs):
		with file(filename, 'rb') as f:
			csv_rows = self.unicode_csv_reader(f, dialect=dialect, **kwargs)
			header = csv_rows.next()
			for row in csv_rows:
				if len(row) > 0:
					rowdict = dict(zip(header, row))
					yield rowdict

	def unicode_csv_reader(self, utf8_data, dialect=csv.excel, **kwargs):
		csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
		for row in csv_reader:
			yield [unicode(cell, 'utf-8') for cell in row]

	def update_progress(self):
		if self.track_progress:
			if not self.progress_initialized:
				self.progress_filename = os.path.join(self.out_dir, self.name + self.collection + "progress.txt")
				self.progress_file = file(self.progress_filename, 'w')
				self.count = 0
				self.total = len(self.files)

			self.count += 1
			self.progress_file.write('<' + str(self.count*1000.0/float(self.total)) + '>\n')
			self.progress_file.flush()

	def write_html(self, params):
		logging.info("writing HTML")
		params.update({"COLLECTION_NAME": self.collection_name})
		try:
			template_filename = getattr(self, "template_filename", os.path.join(self.cwd, "templates", self.name + ".html"))
			additional_arg_str = "_" + "_".join([urllib.quote(x) for x in self.extra_args]) if len(self.extra_args) > 0 else ""
			out_filename = getattr(self, "out_filename", os.path.join(self.out_dir, self.name + self.collection + additional_arg_str + ".html"))
			with file(out_filename, 'w') as outfile:
				with file(template_filename) as template:
					template_str = template.read()
					for k, v in params.iteritems():
						template_str = template_str.replace(k, v)
					outfile.write(template_str)
		except:
			logging.error(traceback.format_exc())

	def process(self):
		"""
		Example process -- should be overridden
		"""
		output = file(os.path.join(self.out_dir, self.name + '.txt'), 'w')
		for filename in self.files:
			output.write(' '.join([filename, self.metadata[filename]]) + '\n')
		output.close()

if __name__ == "__main__":
	try:
		logging.basicConfig(filename=os.path.join(sys.argv[3], "logs", "textprocessor.log"), level=logging.INFO)
		processor = TextProcessor(sys.argv, track_progress = True)
		processor.process()
	except:
		logging.error(traceback.format_exc())