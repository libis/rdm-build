#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'csv'

class MetadataProperties

  attr_reader :input_file, :output_file
  attr_reader :section, :header, :prefix

  def initialize(metadata_tsv_file, properties_file)
    @input_file = metadata_tsv_file
    @output_file = properties_file
  end

  def process
    File.open(output_file, 'wt') do |f|
      CSV.foreach(ARGV[0], col_sep: "\t", liberal_parsing: true) do |row|
        if row[0] =~ /^#(.*)$/
          @header = row
          @section = $1
          next
        end
        next if @section&.empty?
        case @section
        when 'metadataBlock'
          @prefix = 'metadatablock.'
          w f, row, 'name'
          w f, row, 'displayName'
        when 'datasetField'
          @prefix = "datasetfieldtype.#{row[header.index('name')]}."
          w f, row, 'title'
          w f, row, 'description'
          w f, row, 'watermark'
        when 'controlledVocabulary'
          @prefix = "controlledvocabulary.#{row[header.index('DatasetField')]}."
          v = value(row, 'Value')
          write_line f, v, v
        else
        end
      end
    end
  end

  private

  def value(row, field_name)
    row[header.index(field_name)]
  end

  def sanitize(text)
    text&.unicode_normalize(:nfd).to_s.codepoints.delete_if {|c| c > 255}.map(&:chr).join.gsub(/\s+/, '_').downcase
  end

  def normalize(text)
    text&.unicode_normalize(:nfc).to_s.codepoints.map {|c| c > 127 ? "\\u%4.4X" % c : c.chr}.join
  end
  
  def w(f, row, field_name)
    write_line f, field_name, value(row, field_name)
  end

  def write_line(f, field_name, field_value)
    f.puts "%s#{sanitize(field_name)}=%s" % [ prefix, normalize(field_value) ]
  end

end

unless ARGV.size == 2
  puts "Usage: #{$PROGRAM_NAME} <metadata tsv file> <properties file>"
  exit 0
end

MetadataProperties.new(ARGV[0], ARGV[1]).process
