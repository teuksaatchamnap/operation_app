<?php

namespace App\Mail;

use App\Models\Sample;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class QualityAlertEmail extends Mailable
{
    use Queueable, SerializesModels;

    /**
     * Create a new message instance.
     */
    public function __construct(
        public Sample $sample,
    )
    {}

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        $risk = max([$this->sample->contamination_level_bottle, $this->sample->contamination_level_machine]);
        return new Envelope(
            subject: 'Level '.$risk.' water quality alert for site '.$this->sample->site,
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        $p= "";
        if($this->sample->resultMachine ==1)
        {
            $p= 'emails.newWQEmails.machine1';
        }
        if($this->sample->resultMachine ==2)
        {
            $p= 'emails.newWQEmails.machine2';
        }
        if($this->sample->resultMachine ==3)
        {
            $p= 'emails.newWQEmails.machine3';
        }
        if($this->sample->resultBottle ==1)
        {
            $p= 'emails.newWQEmails.bottle1';
        }
        if($this->sample->resultBottle ==2)
        {
            $p= 'emails.newWQEmails.bottle2';
        }
        if($this->sample->resultBottle ==3)
        {
            $p= 'emails.newWQEmails.bottle3';
        }

        return new Content(
            markdown: $p,
        );
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return [];
    }
}
