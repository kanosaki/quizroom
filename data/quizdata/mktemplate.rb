#!/usr/bin/env ruby
require 'fileutils'

NUMBAR_OF_QUIZES = 10
NUMBER_OF_CHOICES = 4
QUIZ_FILENAME = "quiz.html"
CHOICES_DIRNAME = "choices"

1.step(NUMBAR_OF_QUIZES).each do |dir_id|
  quiz_dirname = sprintf("%02d", dir_id)
  Dir.mkdir(quiz_dirname)
  quiz_filepath = File.join(quiz_dirname, QUIZ_FILENAME)
  FileUtils.touch(quiz_filepath)
  choice_dirpath = File.join(quiz_dirname, CHOICES_DIRNAME)
  Dir.mkdir(choice_dirpath)
  1.step(NUMBER_OF_CHOICES).each do |choice_id|
    choice_filename = sprintf("%02d", choice_id)
    choice_filepath = File.join(quiz_dirname, CHOICES_DIRNAME, "#{choice_filename}.html")
    FileUtils.touch(choice_filepath)
  end
end
