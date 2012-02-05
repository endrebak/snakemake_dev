import sys, os, time, stat, traceback
from snakemake.exceptions import MissingOutputException, RuleException, print_exception

class protected(str):
	"""
	A string that describes a path to a file that shall be write-protected.
	"""
	pass

def run_wrapper(run, rulename, ruledesc, input, output, wildcards, rowmap):
	"""
	Wrapper around the run method that handles directory creation and output file deletion on error.
	
	Arguments
	run -- the run method
	input -- list of input files
	output -- list of output files
	wildcards -- so far processed wildcards
	"""
	print(ruledesc)

	for o in output:
		dir = os.path.dirname(o)
		if len(dir) > 0 and not os.path.exists(dir):
			os.makedirs(dir)
	try:
		t0 = time.time()
		run(input, output, wildcards)
		runtime = time.time() - t0
		for o in output:
			if not os.path.exists(o):
				raise MissingOutputException("Output file {} not produced by rule {}.".format(o, rulename))
			else:
				if isinstance(o, protected):
					mode = os.stat(o).st_mode
					os.chmod(o, mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
		return runtime
	except (Exception, BaseException) as ex:
		print_exception(ex, rowmap)
		
		# Remove produced output on exception
		for o in output:
			if os.path.exists(o) and not os.path.isdir(o): os.remove(o)
		for o in output:
			if os.path.exists(o) and os.path.isdir(o) and not os.listdir(o): os.rmdir(o)
		raise Exception()

class Job:
	def __init__(self, workflow, rule = None, message = None, input = None, output = None, wildcards = None, depends = set(), dryrun = False, needrun = True):
		self.rule, self.message, self.input, self.output, self.wildcards = rule, message, input, output, wildcards
		self.dryrun, self.needrun = dryrun, needrun
		self.depends = depends
		self._callbacks = list()
		self.workflow = workflow
		self._queued = False
		self._finished = False
	
	def run(self, callback = None):
		if callback:
			if self._finished:
				callback(self)
				return
			self._callbacks.append(callback)
		if not self._queued:
			self._queued = True
			if self.depends:
				for job in list(self.depends):
					if job in self.depends:
						job.run(callback = self._wakeup_if_ready)
			else:
				self._wakeup()
	
	def _wakeup_if_ready(self, job):
		if job in self.depends:
			self.depends.remove(job)
		if not self.depends:
			self._wakeup()
	
	def _wakeup(self):
		if self.rule.has_run() and self.needrun:
			if self.dryrun:
				print(self.message)
				self._wakeup_waiting()
			else:
				self.workflow.get_pool().apply_async(
					run_wrapper, 
					(self.rule.get_run(), self.rule.name, self.message, self.input, self.output, self.wildcards, self.workflow.rowmap), 
					callback=self._finished_callback, 
					error_callback=self._raise_error
				)
		else:
			self._wakeup_waiting()
	
	def _finished_callback(self, value = None):
		self.workflow.jobcounter.done()
		print(self.workflow.jobcounter)
		self._finished = True
		if value != None:
			self.workflow.report_runtime(self.rule, value)
		self._wakeup_waiting()
		
	def _wakeup_waiting(self):
		for callback in self._callbacks:
			callback(self)
	
	def _raise_error(self, error):
		# simply stop because exception was printed in run_wrapper
		self.workflow.set_jobs_finished()