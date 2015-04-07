package edu.utk.eecs.cs560.pa2; //This is how to Java

import java.io.*;
import java.util.*;
import java.util.regex.*;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.filecache.DistributedCache;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.util.*;
public class InvertedIndex extends Configured implements Tool {
	public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text> {
		static enum Counters { INPUT_WORDS }
		//private final static IntWritable one = new IntWritable(1);
		
		private Text word = new Text();
		private Text offset;
		private boolean caseSensitive = false;
		private Set<String> patternsToSkip = new HashSet<String>();
		private long numRecords = 0;
		private String inputFile;
		public void configure(JobConf job) {
		//caseSensitive = job.getBoolean("wordcount.case.sensitive", true);
			inputFile = job.get("map.input.file");
			if (job.getBoolean("wordcount.skip.patterns", false)) {
					Path[] patternsFiles = new Path[0];
					try {
							patternsFiles = DistributedCache.getLocalCacheFiles(job);
					} catch (IOException ioe) {
							System.err.println("Caught exception while getting cached files: " + StringUtils.stringifyException(ioe));
					}
					for (Path patternsFile : patternsFiles) {
							parseSkipFile(patternsFile);
					}
			}
		}
		private void parseSkipFile(Path patternsFile) {
			try {
					BufferedReader fis = new BufferedReader(new FileReader(patternsFile.toString()));
					String pattern = null;
					while ((pattern = fis.readLine()) != null) {
							patternsToSkip.add(pattern);
					}
			} catch (IOException ioe) {
					System.err.println("Caught exception while parsing the cached file '" + patternsFile + "' : " + StringUtils.stringifyException(ioe));
			}
		}
		public String removePunctuation(String word) {
			String result = word;
			result = result.replaceFirst("^[^A-Za-z]+", "");
			result = result.replaceAll("[^A-Za-z]+$", "");
			return result;
		}
		public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
			String line = (caseSensitive) ? value.toString() : value.toString().toLowerCase();
			for (String pattern : patternsToSkip) {
					line = line.replaceAll(pattern, "");
			}
			StringTokenizer tokenizer = new StringTokenizer(line);
			int i = 0;
			String tmp = new String();
			while (tokenizer.hasMoreTokens()) {
					if (i == 0)
						tmp = tokenizer.nextToken() + "-";
					if (i == 1)
						tmp += tokenizer.nextToken() + "-";
					if (i > 1) {
						word.set(removePunctuation(tokenizer.nextToken()));
						offset = new Text(tmp + (i-2));
						output.collect(word, offset);
						reporter.incrCounter(Counters.INPUT_WORDS, 1);
					}
					i++;
			}
			if ((++numRecords % 100) == 0) {
					reporter.setStatus("Finished processing " + numRecords + " records " + "from the input file: " + inputFile);
			}
		}
	}
	public static class Reduce extends MapReduceBase implements Reducer<Text, Text, Text, Text> {
		private ArrayList<String> temp;
		//threshold determined in word count step
		private static final int threshold = 2000;

		public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
			temp = new ArrayList<String>();
			while (values.hasNext()) {
				temp.add(values.next().toString());
			}
			if (temp.size() < threshold) {
				Iterator<String> it = temp.iterator();
				while(it.hasNext()) {
					output.collect(key, new Text(it.next()));
				}
			}
		}
	}
	public int run(String[] args) throws Exception {
			JobConf conf = new JobConf(getConf(), InvertedIndex.class);
			conf.setJobName("inverted-index");
			conf.setOutputKeyClass(Text.class);
			conf.setOutputValueClass(Text.class);
			conf.setMapperClass(Map.class);
			conf.setCombinerClass(Reduce.class);
			conf.setReducerClass(Reduce.class);
			conf.setInputFormat(TextInputFormat.class);
			conf.setOutputFormat(TextOutputFormat.class);
			List<String> other_args = new ArrayList<String>();
			for (int i=0; i < args.length; ++i) {
					if ("-skip".equals(args[i])) {
							DistributedCache.addCacheFile(new Path(args[++i]).toUri(), conf);
							conf.setBoolean("wordcount.skip.patterns", true);
					} else {
							other_args.add(args[i]);
					}
			}
			FileInputFormat.setInputPaths(conf, new Path(other_args.get(0)));
			FileOutputFormat.setOutputPath(conf, new Path(other_args.get(1)));
			JobClient.runJob(conf);
			return 0;
	}
	public static void main(String[] args) throws Exception {
			int res = ToolRunner.run(new Configuration(), new InvertedIndex(), args);
			System.exit(res);
	}
}
